# -*- coding: utf-8 -*-
# This component is derived from PCSE software/Wofost model
# (Copyright @ 2004-2014 Alterra, Wageningen-UR; Allard de Wit allard.dewit@wur.nl, April 2014)
# and modified by EC-JRC for the eCrops framework under the European Union Public License (EUPL), Version 1.2
# European Commission, Joint Research Centre, March 2023



from array import array
from collections import deque

from ecrops.wofost_util.util import limit

import ecrops.wofost_util.Afgen
from ..Printable import Printable
from ecrops.Step import Step

class WOFOST_Leaf_Dynamics(Step):
    """Leaf dynamics for the WOFOST crop model.

    Implementation of biomass partitioning to leaves, growth and senenscence
    of leaves. WOFOST keeps track of the biomass that has been partitioned to
    the leaves for each day (variable `LV`), which is called a leaf class).
    For each leaf class the leaf age (variable 'LVAGE') and specific leaf area
    (variable `SLA`) are also registered. Total living leaf biomass is
    calculated by summing the biomass values for all leaf classes. Similarly,
    leaf area is calculated by summing leaf biomass times specific leaf area
    (`LV` * `SLA`).

    Senescense of the leaves can occur as a result of physiological age,
    drought stress or self-shading.

    *Simulation parameters* (provide in cropdata dictionary)

    =======  ============================================= =======  ============
     Name     Description                                   Type     Unit
    =======  ============================================= =======  ============
    RGRLAI   Maximum relative increase in LAI.              SCr     ha ha-1 d-1
    SPAN     Life span of leaves growing at 35 Celsius      SCr     d
    TBASE    Lower threshold temp. for ageing of leaves     SCr     C
    PERDL    Max. relative death rate of leaves due to      SCr
             water stress
    TDWI     Initial total crop dry weight                  SCr     kg ha-1
    KDIFTB   Extinction coefficient for diffuse visible     TCr
             light as function of DVS
    SLATB    Specific leaf area as a function of DVS        TCr     ha kg-1
    =======  ============================================= =======  ============

    *State variables*

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    LV       Leaf biomass per leaf class                        N    kg ha-1
    SLA      Specific leaf area per leaf class                  N    ha kg-1
    LVAGE    Leaf age per leaf class                            N    d
    LVSUM    Sum of LV                                          N    kg ha-1
    LAIEM    LAI at emergence                                   N    -
    LASUM    Total leaf area as sum of LV*SLA,                  N    -
             not including stem and pod area                    N
    LAIEXP   LAI value under theoretical exponential growth     N    -
    LAIMAX   Maximum LAI reached during growth cycle            N    -
    LAI      Leaf area index, including stem and pod area       Y    -
    WLV      Dry weight of living leaves                        Y    kg ha-1
    DWLV     Dry weight of dead leaves                          N    kg ha-1
    TWLV     Dry weight of total leaves (living + dead)         Y    kg ha-1
    TAGP     Total above - ground biomass                       N    kg ha-1
    =======  ================================================= ==== ============


    *Rate variables*

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    GRLV     Growth rate leaves                                 N   kg ha-1 d-1
    DSLV1    Death rate leaves due to water stress              N   kg ha-1 d-1
    DSLV2    Death rate leaves due to self-shading              N   kg ha-1 d-1
    DSLV3    Death rate leaves due to frost kill                N   kg ha-1 d-1
    DSLV     Maximum of DLSV1, DSLV2, DSLV3                     N   kg ha-1 d-1
    DALV     Death rate leaves due to aging.                    N   kg ha-1 d-1
    DRLV     Death rate leaves as a combination of DSLV and     N   kg ha-1 d-1
             DALV
    SLAT     Specific leaf area for current time step,          N   ha kg-1
             adjusted for source/sink limited leaf expansion
             rate.
    FYSAGE   Increase in physiological leaf age                 N   -
    GLAIEX   Sink-limited leaf expansion rate (exponential      N   ha ha-1 d-1
             curve)
    GLASOL   Source-limited leaf expansion rate (biomass        N   ha ha-1 d-1
             increase)
    =======  ================================================= ==== ============


    *External dependencies:*

    ======== ============================== =============================== ===========
     Name     Description                         Provided by               Unit
    ======== ============================== =============================== ===========
    DVS      Crop development stage         DVS_Phenology                    -
    FL       Fraction biomass to leaves     DVS_Partitioning                 -
    FR       Fraction biomass to roots      DVS_Partitioning                 -
    SAI      Stem area index                WOFOST_Stem_Dynamics             -
    PAI      Pod area index                 WOFOST_Storage_Organ_Dynamics    -
    TRA      Transpiration rate             Evapotranspiration              cm day-1
    TRAMX    Maximum transpiration rate     Evapotranspiration              cm day-1
    ADMI     Above-ground dry matter        CropSimulation                  kg ha-1 d-1
             increase
    RF_FROST Reduction factor frost kill    FROSTOL                          -
    ======== ============================== =============================== ===========
    """

    def getparameterslist(self):
        return {
            "RGRLAI": {"Description": "Maximum relative increase in LAI.", "Type": "Number",
                       "Mandatory": "True",
                       "UnitOfMeasure": "ha / ha day"},
            "SPAN": {"Description": "Life span of leaves growing at 35 Celsius", "Type": "Number",
                     "Mandatory": "True",
                     "UnitOfMeasure": "day"},
            "TBASE": {"Description": "Lower threshold temp. for ageing of leaves", "Type": "Number",
                      "Mandatory": "True",
                      "UnitOfMeasure": "C"},
            "PERDL": {"Description": "Max. relative death rate of leaves due to water stress", "Type": "Number",
                      "Mandatory": "True",
                      "UnitOfMeasure": "unitless"},
            "TDWI": {"Description": "Initial total crop dry weight ", "Type": "Number",
                     "Mandatory": "True",
                     "UnitOfMeasure": "Kg/ha"},
            "SLATB": {"Description": "Specific leaf area as a function of DVS", "Type": "Number",
                      "Mandatory": "True",
                      "UnitOfMeasure": "ha/Kg"},
            "KDIFTB": {"Description": "Extinction coefficient for diffuse visible light as function of DVS",
                       "Type": "Number",
                       "Mandatory": "True",
                       "UnitOfMeasure": "unitless"},
            "ThresholdTemperatureForHeatStressEffectOnSenescence": {
                "Description": "Threshold temperature for heat stress effect on senescence",
                "Type": "Number",
                "Mandatory": "True",
                "UnitOfMeasure": "C"},
            "ConsiderHeatStressEffectOnSenescence": {
                "Description": "Boolean. True to consider the heat stress effect on senescence",
                "Type": "String",
                "Mandatory": "True",
                "UnitOfMeasure": "unitless"}

        }

    def setparameters(self, status):
        status.leafdinamics = Printable()
        status.leafdinamics.params = Printable()
        cropparams = status.allparameters
        status.leafdinamics.params.RGRLAI = cropparams['RGRLAI']
        status.leafdinamics.params.SPAN = cropparams['SPAN']
        status.leafdinamics.params.TBASE = cropparams['TBASE']
        status.leafdinamics.params.PERDL = cropparams['PERDL']
        status.leafdinamics.params.TDWI = cropparams['TDWI']
        status.leafdinamics.params.SLATB = ecrops.wofost_util.Afgen.Afgen(cropparams['SLATB'])
        status.leafdinamics.params.KDIFTB = ecrops.wofost_util.Afgen.Afgen(cropparams['KDIFTB'])

        if hasattr(status, 'ConsiderHeatStressEffectOnSenescence'):
            status.leafdinamics.params.ConsiderHeatStressEffectOnSenescence = status.ConsiderHeatStressEffectOnSenescence
        else:
            status.leafdinamics.params.ConsiderHeatStressEffectOnSenescence = False  # False by default

        if hasattr(status, 'ThresholdTemperatureForHeatStressEffectOnSenescence'):
            status.leafdinamics.params.ThresholdTemperatureForHeatStressEffectOnSenescence = status.ThresholdTemperatureForHeatStressEffectOnSenescence
        else:
            status.leafdinamics.params.ThresholdTemperatureForHeatStressEffectOnSenescence = 1000

        return status

    def initialize(self, status):

        # Initial leaf biomass
        status.states.WLV = 0
        status.states.DWLV = 0.
        status.states.TWLV = 0
        status.states.TAGP = 0.0
        # First leaf class (SLA, age and weight)
        status.states.SLA = []
        status.states.LVAGE = []
        status.states.LV = []
        status.states.TWST =0
        status.states.TWSO=0

        # Initial values for leaf area
        status.states.LAIEM = 0
        status.states.LASUM = 0
        status.states.LAIEXP = 0
        status.states.LAIMAX = 0
        status.states.LAI = 0

        status.rates.DRLV = 0.
        status.rates.GRLV = 0.
        status.rates.DSLV1 = 0
        status.rates.DSLV2 = 0
        status.rates.DSLV3 = 0
        status.states.LAICR = 0
        status.rates.FYSAGE = 0
        status.rates.SLAT = 0
        status.rates.GLAIEX = 0
        status.rates.GLASOL = 0

        status.states.DeadLeavesBiomassDueToSenescenceIncreaseByHeatStress = 0
        status.states.DeadLeavesBiomassDueToSenescence = 0
        status.states.DeadLeavesBiomassDueToSenescenceWithoutEffectOfHeatStress = 0
        status.rates.factorToIncreaseSenescenceForHeatStress = 1;

        status.states.TAGP_previousday = 0
        status.rates.DALV = 0
        status.rates.DALV_Original = 0

        return status

    def _calc_LAI(self, status):
        # Total leaf area Index as sum of leaf, pod and stem area
        return status.states.LASUM + status.states.SAI + status.states.PAI

    def runstep(self, status):

        rates = status.rates
        states = status.states
        params = status.leafdinamics.params
        status.rates.DRLV = 0.
        status.rates.GRLV = 0.
        status.rates.DSLV1 = 0
        status.rates.DSLV2 = 0
        status.rates.DSLV3 = 0
        status.rates.FYSAGE = 0
        status.rates.SLAT = 0
        status.rates.GLAIEX = 0


        # CALCULATE INITIAL STATE VARIABLES at sowing/emergence day
        if status.day == status.states.DOS or status.day == status.states.DOE:
            params = status.leafdinamics.params
            FL = status.states.FL
            FR = status.states.FR
            DVS = status.states.DVS

            # Initial leaf biomass
            status.states.WLV = (params.TDWI * (1 - FR)) * FL
            status.states.DWLV = 0.
            status.states.TWLV = status.states.WLV + status.states.DWLV
            status.states.TAGP = 0.0
            # First leaf class (SLA, age and weight)
            status.states.SLA = deque([params.SLATB(DVS)])
            status.states.LVAGE = deque([0.])
            status.states.LV = deque([status.states.WLV])

            # Initial values for leaf area
            status.states.LAIEM = status.states.LV[0] * status.states.SLA[0]
            status.states.LASUM = status.states.LAIEM
            status.states.LAIEXP = status.states.LAIEM
            status.states.LAIMAX = status.states.LAIEM
            status.states.LAI = status.states.LASUM + status.states.SAI + status.states.PAI

        if (states.DOE is None or status.day < states.DOE) or (states.DOE is not None and status.day >= states.DOE and (
                states.DOM is not None and status.day >= states.DOM)):  # execute only after emergence and before maturity
            return status

        # Growth rate leaves
        # weight of new leaves
        ADMI = status.rates.ADMI
        FL = status.states.FL
        rates.GRLV = ADMI * FL

        # death of leaves due to water stress
        TRA = status.rates.TRA
        TRAMX = status.rates.TRAMX
        rates.DSLV1 = states.WLV * (1. - TRA / TRAMX) * params.PERDL

        # death due to self shading cause by high LAI
        DVS = status.states.DVS
        status.states.LAICR = 3.2 / params.KDIFTB(DVS)
        rates.DSLV2 = states.WLV * limit(0., 0.03, 0.03 * (states.LAI - status.states.LAICR) / status.states.LAICR)

        rates.DSLV3 = 0.

        # leaf death equals maximum of water stress, shading and frost
        rates.DSLV = max(rates.DSLV1, rates.DSLV2, rates.DSLV3)

        # Determine how much leaf biomass classes have to die in states.LV,
        # given the a life span > SPAN, these classes will be accumulated
        # in DALV.
        # Note that the actual leaf death is imposed on the array LV during the
        # state integration step.
        DALV = 0.0
        for lv, lvage in zip(states.LV, states.LVAGE):
            if lvage > params.SPAN:
                DALV += lv
        rates.DALV = DALV

        # added from 22-October-2019 - implementation of heat stress effect impact in Wofost, using the senescence START
        # senescence is increased by a factor due to temperature

        rates.factorToIncreaseSenescenceForHeatStress = 1;
        if (
                params.ConsiderHeatStressEffectOnSenescence and status.states.TEMP_MAX > params.ThresholdTemperatureForHeatStressEffectOnSenescence):
            rates.factorToIncreaseSenescenceForHeatStress = 4 - (
                        1 - (status.states.TEMP_MAX - params.ThresholdTemperatureForHeatStressEffectOnSenescence) / 2)
        rates.DALV_Original = rates.DALV
        rates.DALV = rates.DALV * rates.factorToIncreaseSenescenceForHeatStress

        # added from 22-October-2019 - implementation of heat stress effect impact in Wofost, using the senescence END

        # Total death rate leaves
        rates.DRLV = max(rates.DSLV, rates.DALV)

        # physiologic ageing of leaves per time step
        # avg_temperature=status.states.TEMP  #davide 19-10-2021, as in bioma, we dont use the TEMP (avg temparature) variable, but we use (tmax+tmin)/2. Time to time there are differences
        avg_temperature = (status.states.TEMP_MAX + status.states.TEMP_MIN) / 2.
        rates.FYSAGE = max(0., (avg_temperature - params.TBASE) / (35. - params.TBASE))

        # specific leaf area of leaves per time step
        rates.SLAT = params.SLATB(DVS)

        # leaf area not to exceed exponential growth curve
        if (states.LAIEXP < 6.):
            DTEFF = max(0., status.states.TEMP - params.TBASE)
            rates.GLAIEX = states.LAIEXP * params.RGRLAI * DTEFF
            # source-limited increase in leaf area
            rates.GLASOL = rates.GRLV * rates.SLAT
            # sink-limited increase in leaf area
            GLA = min(rates.GLAIEX, rates.GLASOL)
            # adjustment of specific leaf area of youngest leaf class
            if (rates.GRLV > 0.):
                rates.SLAT = GLA / rates.GRLV

        return status

    def integrate(self, status):

        rates = status.rates
        states = status.states



        # --------- leave death ---------
        tLV = array('d', states.LV)
        tSLA = array('d', states.SLA)
        tLVAGE = array('d', states.LVAGE)
        tDRLV = rates.DRLV

        # leaf death is imposed on leaves by removing leave classes from the
        # right side of the deque.
        for LVweigth in reversed(states.LV):
            if tDRLV > 0.:
                if tDRLV >= LVweigth:  # remove complete leaf class from deque
                    tDRLV -= LVweigth
                    tLV.pop()
                    tLVAGE.pop()
                    tSLA.pop()
                else:  # Decrease value of oldest (rightmost) leave class
                    tLV[-1] -= tDRLV
                    tDRLV = 0.
            else:
                break

        # Integration of physiological age
        tLVAGE = deque([age + rates.FYSAGE for age in tLVAGE])
        tLV = deque(tLV)
        tSLA = deque(tSLA)

        # --------- leave growth ---------
        # new leaves in class 1
        tLV.appendleft(rates.GRLV)
        tSLA.appendleft(rates.SLAT)
        tLVAGE.appendleft(0.)

        # calculation of new leaf area
        states.LASUM = sum([lv * sla for lv, sla in zip(tLV, tSLA)])
        states.LAI = self._calc_LAI(status)
        states.LAIMAX = max(states.LAI, states.LAIMAX)

        # exponential growth curve
        states.LAIEXP += rates.GLAIEX

        # Update leaf biomass states
        states.WLV = sum(tLV)
        states.DWLV += rates.DRLV
        states.TWLV = states.WLV + states.DWLV

        # Store final leaf biomass deques
        status.states.LV = tLV
        status.states.SLA = tSLA
        status.states.LVAGE = tLVAGE

        # added from 22-October-2019 - implementation of heat stress effect impact in Wofost, using the senescence START
        status.states.DeadLeavesBiomassDueToSenescence = status.states.DeadLeavesBiomassDueToSenescence + rates.DALV
        states.DeadLeavesBiomassDueToSenescenceIncreaseByHeatStress = states.DeadLeavesBiomassDueToSenescenceIncreaseByHeatStress + (
                    rates.DALV - status.rates.DALV_Original)
        states.DeadLeavesBiomassDueToSenescenceWithoutEffectOfHeatStress = states.DeadLeavesBiomassDueToSenescence - states.DeadLeavesBiomassDueToSenescenceIncreaseByHeatStress
        # added from 22-October-2019 - implementation of heat stress effect impact in Wofost, using the senescence END

        # Initial total (living+dead) above-ground biomass of the crop
        # Total        above - ground                N | kg/    ha - 1
        status.states.TAGP_previousday = status.states.TAGP
        status.states.TAGP = status.states.TWLV + status.states.TWST + status.states.TWSO

        return status

    # NOT USED
    def _set_variable_LAI(self, status, nLAI):
        """Updates the value of LAI to to the new value provided as input.

        Related state variables will be updated as well and the increments
        to all adjusted state variables will be returned as a dict.
        """
        states = status.states

        # Store old values of states
        oWLV = states.WLV
        oLAI = states.LAI
        oTWLV = states.TWLV
        oLASUM = states.LASUM

        # Reduce oLAI for pod and stem area. SAI and PAI will not be adjusted
        # because this is often only a small component of the total leaf
        # area. For all current crop files in WOFOST SPA and SSA are zero
        # anyway
        SAI = states.SAI
        PAI = states.PAI
        adj_nLAI = max(nLAI - SAI - PAI, 0.)
        adj_oLAI = max(oLAI - SAI - PAI, 0.)

        # LAI Adjustment factor for leaf biomass LV (rLAI)
        if adj_oLAI > 0:
            rLAI = adj_nLAI / adj_oLAI
            LV = [lv * rLAI for lv in states.LV]
        # If adj_oLAI == 0 then add the leave biomass directly to the
        # youngest leave age class (LV[0])
        else:
            LV = [nLAI / states.SLA[0]]

        states.LASUM = sum([lv * sla for lv, sla in zip(LV, states.SLA)])
        states.LV = deque(LV)
        states.LAI = self._calc_LAI()
        states.WLV = sum(states.LV)
        states.TWLV = states.WLV + states.DWLV

        increments = {"LAI": states.LAI - oLAI,
                      "LAISUM": states.LASUM - oLASUM,
                      "WLV": states.WLV - oWLV,
                      "TWLV": states.TWLV - oTWLV}
        return increments

    def getinputslist(self):
        return {
            "day": {"Description": "Current day", "Type": "Number", "UnitOfMeasure": "doy",
                    "StatusVariable": "status.day"},
            "DOS": {"Description": "Doy of sowing", "Type": "Number", "UnitOfMeasure": "doy",
                    "StatusVariable": "status.states.DOS"},
            "DOE": {"Description": "Doy of emergence", "Type": "Number", "UnitOfMeasure": "doy",
                    "StatusVariable": "status.states.DOE"},
            "DOM": {"Description": "Doy of maturity", "Type": "Number", "UnitOfMeasure": "doy",
                    "StatusVariable": "status.states.DOM"},
            "TEMP": {"Description": "Average daily temperature", "Type": "Number", "UnitOfMeasure": "C",
                     "StatusVariable": "status.states.TEMP"},
            "TEMP_MIN": {"Description": "Minimum temperature",
                         "Type": "Number", "UnitOfMeasure": "C",
                         "StatusVariable": "status.states.TEMP_MIN"},
            "TEMP_MAX": {"Description": "Maximum temperature",
                         "Type": "Number", "UnitOfMeasure": "C",
                         "StatusVariable": "status.states.TEMP_MAX"},
            "DVS": {"Description": "Development stage", "Type": "Number", "UnitOfMeasure": "unitless",
                    "StatusVariable": "status.states.DVS"},
            "TRA": {"Description": "Actual transpiration rate from the plant canopy", "Type": "Number",
                    "UnitOfMeasure": "cm/day",
                    "StatusVariable": "status.rates.TRA"},
            "TRAMX": {"Description": "Max transpiration rate from the plant canopy", "Type": "Number",
                      "UnitOfMeasure": "cm/day",
                      "StatusVariable": "status.rates.TRAMX"},
            "FL": {"Description": "Partitioning to leaves", "Type": "Number", "UnitOfMeasure": "unitless",
                   "StatusVariable": "status.states.FL"},
            "FR": {"Description": "Partitioning to roots", "Type": "Number", "UnitOfMeasure": "unitless",
                   "StatusVariable": "status.states.FR"},
            "ADMI": {"Description": "Daily increase in above-ground dry matter", "Type": "Number",
                     "UnitOfMeasure": "Kg/ha",
                     "StatusVariable": "status.rates.ADMI"},
            "WLV": {"Description": " Dry weight of living leaves", "Type": "Number", "UnitOfMeasure": "Kg/ha",
                    "StatusVariable": "status.states.WLV"},
            "DWLV": {"Description": "Dry weight of dead leaves", "Type": "Number", "UnitOfMeasure": "Kg/ha",
                     "StatusVariable": "status.states.DWLV"},
            "TWLV": {"Description": "Total weight dry + living leaves", "Type": "Number", "UnitOfMeasure": "Kg/ha",
                     "StatusVariable": "status.states.TWLV"},
            "LV": {"Description": "List containing the biomass of the leaves for each day (one value per day)",
                   "Type": "Array of numbers",
                   "UnitOfMeasure": "Kg/ha",
                   "StatusVariable": "status.states.LV"},
            "SLA": {
                "Description": "List containing the SLA (Specific leaf area) of the leaves for each day (one value per day)",
                "Type": "Array of numbers",
                "UnitOfMeasure": "ha/kg",
                "StatusVariable": "status.states.SLA"},
            "LVAGE": {"Description": "List containing the age of the leaves for each day (one value per day)",
                      "Type": "Array of numbers",
                      "UnitOfMeasure": "degree days",
                      "StatusVariable": "status.states.LVAGE"},
            "PAI": {"Description": "Pod area index",
                    "Type": "Number", "UnitOfMeasure": "unitless",
                    "StatusVariable": "status.states.PAI"},
            "SAI": {"Description": "Stem area index",
                    "Type": "Number", "UnitOfMeasure": "unitless",
                    "StatusVariable": "status.states.SAI"},
            "LAIMAX": {"Description": "Maximum value of LAI during the season", "Type": "Number",
                       "UnitOfMeasure": "unitless",
                       "StatusVariable": "status.states.LAIMAX"},
            "LASUM": {"Description": "Total leaf area as sum of LV*SLA, not including stem and pod area",
                      "Type": "Number",
                      "UnitOfMeasure": "unitless",
                      "StatusVariable": "status.states.LASUM"},
            "LAIEXP": {"Description": "LAI value under theoretical exponential growth", "Type": "Number",
                       "UnitOfMeasure": "unitless",
                       "StatusVariable": "status.states.LAIEXP"},
            "TAGP": {"Description": "Total (living+dead) above-ground biomass", "Type": "Number",
                     "UnitOfMeasure": "Kg/ha",
                     "StatusVariable": "status.states.TAGP"},
            "TWST": {"Description": "Total stem biomass", "Type": "Number",
                     "UnitOfMeasure": "Kg/ha",
                     "StatusVariable": "status.states.TWST"},
            "TWSO": {"Description": "Total storage organs biomass", "Type": "Number",
                     "UnitOfMeasure": "Kg/ha",
                     "StatusVariable": "status.states.TWSO"},

        }

    def getoutputslist(self):
        return {
            "LAI": {"Description": "Leaf area index",
                    "Type": "Number", "UnitOfMeasure": "unitless",
                    "StatusVariable": "status.states.LAI"},
            "LAICR": {"Description": "Leaf area index critical",
                    "Type": "Number", "UnitOfMeasure": "unitless",
                    "StatusVariable": "status.states.LAICR"},

            "GRLV": {"Description": "Daily increase of dry weight of living leaves", "Type": "Number",
                     "UnitOfMeasure": "Kg/ha",
                     "StatusVariable": "status.rates.GRLV"},
            "DRLV": {"Description": "Daily increase of dry weight of dead leaves", "Type": "Number",
                     "UnitOfMeasure": "Kg/ha",
                     "StatusVariable": "status.rates.DRRT"},

            "WLV": {"Description": " Dry weight of living leaves", "Type": "Number", "UnitOfMeasure": "Kg/ha",
                    "StatusVariable": "status.states.WLV"},
            "DWLV": {"Description": "Dry weight of dead leaves", "Type": "Number", "UnitOfMeasure": "Kg/ha",
                     "StatusVariable": "status.states.DWLV"},
            "TWLV": {"Description": "Total weight dry + living leaves", "Type": "Number", "UnitOfMeasure": "Kg/ha",
                     "StatusVariable": "status.states.TWLV"},


            "TAGP": {"Description": "Total (living+dead) above-ground biomass", "Type": "Number", "UnitOfMeasure": "Kg/ha",
                     "StatusVariable": "status.states.TAGP"},

            "DeadLeavesBiomassDueToSenescence": {"Description": "Dead leaves biomass due to senescence (total)", "Type": "Number",
                     "UnitOfMeasure": "Kg/ha",
                     "StatusVariable": "status.states.DeadLeavesBiomassDueToSenescence"},
            "DeadLeavesBiomassDueToSenescenceIncreaseByHeatStress": {"Description": "Increase in dead leaves biomass due to senescence caused by heat stress", "Type": "Number",
                 "UnitOfMeasure": "Kg/ha",
                 "StatusVariable": "status.states.DeadLeavesBiomassDueToSenescenceIncreaseByHeatStress"},
            "DeadLeavesBiomassDueToSenescenceWithoutEffectOfHeatStress": {"Description": "Dead leaves biomass due to senescence (excluded the increase caused by heat stress)", "Type": "Number",
                 "UnitOfMeasure": "Kg/ha",
                 "StatusVariable": "status.states.DeadLeavesBiomassDueToSenescenceWithoutEffectOfHeatStress"},
            "LV": {"Description": "List containing the biomass of the leaves for each day (one value per day)", "Type": "Array of numbers",
                 "UnitOfMeasure": "Kg/ha",
                 "StatusVariable": "status.states.LV"},
            "SLA": {"Description": "List containing the SLA (Specific leaf area) of the leaves for each day (one value per day)", "Type": "Array of numbers",
                 "UnitOfMeasure": "ha/kg",
                 "StatusVariable": "status.states.SLA"},
            "LVAGE": {"Description": "List containing the age of the leaves for each day (one value per day)", "Type": "Array of numbers",
                 "UnitOfMeasure": "degree days",
                 "StatusVariable": "status.states.LVAGE"},
            "LASUM": {"Description": "Total leaf area as sum of LV*SLA, not including stem and pod area", "Type": "Number",
                 "UnitOfMeasure": "unitless",
                 "StatusVariable": "status.states.LASUM"},
            "LAIEXP": {"Description": "LAI value under theoretical exponential growth", "Type": "Number",
                 "UnitOfMeasure": "unitless",
                 "StatusVariable": "status.states.LAIEXP"},
            "LAIMAX": {"Description": "Maximum value of LAI during the season", "Type": "Number",
                 "UnitOfMeasure": "unitless",
                 "StatusVariable": "status.states.LAIMAX"},
            "SLAT": {"Description": "Specific leaf area for current time step, adjusted for source/sink limited leaf expansion rate", "Type": "Number",
                       "UnitOfMeasure": "ha/Kg",
                       "StatusVariable": "status.rates.SLAT"},
            "GLAIEX": {"Description": "Sink-limited leaf expansion rate (exponential curve)", "Type": "Number",
                     "UnitOfMeasure": "ha ha-1 d-1",
                     "StatusVariable": "status.rates.GLAIEX"},
            "GLASOL": {"Description": "Source-limited leaf expansion rate (biomass increase)", "Type": "Number",
                 "UnitOfMeasure": "ha ha-1 d-1",
                 "StatusVariable": "status.rates.GLASOL"},
            "FYSAGE": {"Description": "Increase in physiological leaf age", "Type": "Number",
                 "UnitOfMeasure": "degree days",
                 "StatusVariable": "status.rates.FYSAGE"},
            "DRLV": {"Description": "Death rate leaves as a combination of DSLV and DALV", "Type": "Number",
                 "UnitOfMeasure": "Kg/ha",
                 "StatusVariable": "status.rates.DRLV"},
            "DALV": {"Description": "Death rate leaves due to aging", "Type": "Number",
                 "UnitOfMeasure": "Kg/ha",
                 "StatusVariable": "status.rates.DALV"},
            "DSLV": {"Description": "Maximum of DLSV1, DSLV2, DSLV3", "Type": "Number",
                 "UnitOfMeasure": "Kg/ha",
                 "StatusVariable": "status.rates.DSLV"},
            "DSLV1": {"Description": "Death rate leaves due to water stress", "Type": "Number",
                      "UnitOfMeasure": "Kg/ha",
                      "StatusVariable": "status.rates.DSLV1"},
            "DSLV2": {"Description": " Death rate leaves due to self-shading", "Type": "Number",
                      "UnitOfMeasure": "Kg/ha",
                      "StatusVariable": "status.rates.DSLV2"},
            "DSLV3": {"Description": "Death rate leaves due to frost kill (currently not implemented, always set to 0)", "Type": "Number",
                      "UnitOfMeasure": "Kg/ha",
                      "StatusVariable": "status.rates.DSLV3"},
            "DALV_Original": {"Description": "Death rate leaves due to aging (before heat stress effect)", "Type": "Number",
                 "UnitOfMeasure": "Kg/ha",
                 "StatusVariable": "status.rates.DALV_Original"},
            "factorToIncreaseSenescenceForHeatStress": {"Description": "Factor that increases senescence due to temperature", "Type": "Number",
                 "UnitOfMeasure": "unitless",
                 "StatusVariable": "status.rates.factorToIncreaseSenescenceForHeatStress"},

        }
