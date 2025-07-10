# -*- coding: utf-8 -*-
# This component is derived from PCSE software/Wofost model
# (Copyright @ 2004-2014 Alterra, Wageningen-UR; Allard de Wit allard.dewit@wur.nl, April 2014)
# and modified by EC-JRC for the eCrops framework under the European Union Public License (EUPL), Version 1.2
# European Commission, Joint Research Centre, March 2023


import array
from math import exp

from ecrops.wofost_util.util import limit

import ecrops.wofost_util.Afgen
from ..Printable import Printable
from ecrops.Step import Step

class Evapotranspiration(Step):
    """Calculation of evaporation (water and soil) and transpiration rates.

    Model logic parametrization:
    USE_HERMES_FRROOT if 'False' (default bahaviour), the system use the original FRROOT (root fraction distribution) , based on the ratio between the
    layer depth and the root depth (assuming the roots are equally distributed at every detph). If 'True', it uses a distribution of
    roots factor calculated by HermesRootDepth class. So if USE_HERMES_FRROOT is True, the class HermesRootDepth should be included in the model.

    *Simulation parameters*:

    =======  ============================================= =======  ============
     Name     Description                                   Type     Unit
    =======  ============================================= =======  ============
    CFET     Correction factor for potential transpiration   SCr       -
             rate.
    DEPNR    Dependency number for crop sensitivity to       SCr       -
             soil moisture stress.
    KDIFTB   Extinction coefficient for diffuse visible      TCr       -
             as function of DVS.
    IOX      Switch oxygen stress on (1) or off (0)          SCr       -
    IAIRDU   Switch airducts on (1) or off (0)               SCr       -
    CRAIRC   Critical air content for root aeration          SSo       -
    SM0      Soil porosity                                   SSo       -
    SMW      Volumetric soil moisture content at wilting     SSo       -
             point
    SMCFC    Volumetric soil moisture content at field       SSo       -
             capacity
    SM0      Soil porosity                                   SSo       -
    =======  ============================================= =======  ============


    *State variables*

    Note that these state variables are only assigned after finalize() has been
    run.

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    IDWST     Nr of days with water stress.                      N    -
    IDOST     Nr of days with oxygen stress.                     N    -
    =======  ================================================= ==== ============


    *Rate variables*

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    EVWMX    Maximum evaporation rate from an open water        Y    cm day-1
             surface.
    EVSMX    Maximum evaporation rate from a wet soil surface.  Y    cm day-1
    TRAMX    Maximum transpiration rate from the plant canopy   Y    cm day-1
    TRA      Actual transpiration rate from the plant canopy    Y    cm day-1
    IDOS     Indicates oxygen stress on this day (True|False)   N    -
    IDWS     Indicates water stress on this day (True|False)    N    -
    =======  ================================================= ==== ============



    *External dependencies:*

    =======  =================================== =================  ============
     Name     Description                         Provided by         Unit
    =======  =================================== =================  ============
    DVS      Crop development stage              DVS_Phenology       -
    LAI      Leaf area index                     Leaf_dynamics       -
    SM       Volumetric soil moisture content    Waterbalance        -
    =======  =================================== =================  ============
    """

    def getparameterslist(self):
        return {
            "CFET": {"Description": "Correction factor for potential transpiration rate", "Type": "Number",
                     "Mandatory": "True",
                     "UnitOfMeasure": "unitless"},
            "DEPNR": {"Description": "Dependency number for crop sensitivity to soil moisture stress", "Type": "Number",
                      "Mandatory": "True",
                      "UnitOfMeasure": "unitless"},
            "KDIFTB": {"Description": "Extinction coefficient for diffuse visible as function of DVS", "Type": "Number",
                       "Mandatory": "True",
                       "UnitOfMeasure": "unitless"},
            "IAIRDU": {"Description": "Switch airducts on (1) or off (0)", "Type": "Number", "Mandatory": "True",
                       "UnitOfMeasure": "unitless"},
            "IOX": {"Description": "Switch oxygen stress on (1) or off (0) ", "Type": "Number", "Mandatory": "True",
                    "UnitOfMeasure": "unitless"},
            "CRAIRC": {"Description": "Critical air content for root aeration", "Type": "Number", "Mandatory": "True",
                       "UnitOfMeasure": "unitless"},
            "SM0": {"Description": "Soil porosity", "Type": "Number", "Mandatory": "True",
                    "UnitOfMeasure": "unitless"},
            "SMW": {"Description": "Volumetric soil moisture content at wilting point", "Type": "Number",
                    "Mandatory": "True",
                    "UnitOfMeasure": "unitless"},
            "SMFCF": {"Description": "Volumetric soil moisture content at field capacity", "Type": "Number",
                      "Mandatory": "True",
                      "UnitOfMeasure": "unitless"},
            "num_days_oxygen_shortage": {"Description": "Number of consecutive days after there is the maximum reduction due to oxygen shortage (default = 4)", "Type": "Number",
                      "Mandatory": "True",
                      "UnitOfMeasure": "days"},
            "scaling_factor_oxygen_shortage": {"Description": "Minimum value for reduction factor due to oxygen shortage (default = 0 = maximum reduction)", "Type": "Number",
                      "Mandatory": "True",
                      "UnitOfMeasure": "unitless"}
        }

    def setparameters(self, status):
        status.evapotranspiration = Printable()
        status.evapotranspiration.params = Printable()
        cropparams = status.allparameters
        status.evapotranspiration.params.PerformWaterBalanceStartInAdvance = 'CALC_SOILWATER_BEFORE_SOWING' in status.allparameters and \
                                                                             status.allparameters[
                                                                                 'CALC_SOILWATER_BEFORE_SOWING'] == 1
        status.evapotranspiration.params.PerformWaterBalanceStartInAdvanceUntilSowing = 'CALC_SOILWATER_BEFORE_SOWING' in status.allparameters and \
                                                                                        status.allparameters[
                                                                                            'CALC_SOILWATER_BEFORE_SOWING'] == 3
        status.evapotranspiration.params.USE_HERMES_FRROOT = False
        if hasattr(status, 'USE_HERMES_FRROOT'):
            status.evapotranspiration.params.USE_HERMES_FRROOT = status.USE_HERMES_FRROOT

        if 'num_days_oxygen_shortage' in cropparams:
            status.evapotranspiration.params.num_days_oxygen_shortage = cropparams['num_days_oxygen_shortage']
        else:
            status.evapotranspiration.params.num_days_oxygen_shortage = 4 #original default value
        if 'scaling_factor_oxygen_shortage' in cropparams:
            status.evapotranspiration.params.scaling_factor_oxygen_shortage = cropparams['scaling_factor_oxygen_shortage']
        else:
            status.evapotranspiration.params.scaling_factor_oxygen_shortage = 0 #original default value

        if hasattr(status, 'USE_HERMES_FRROOT'):
            status.evapotranspiration.params.USE_HERMES_FRROOT = status.USE_HERMES_FRROOT
        status.evapotranspiration.params.CFET = cropparams['CFET']
        status.evapotranspiration.params.DEPNR = cropparams['DEPNR']
        status.evapotranspiration.params.KDIFTB = ecrops.wofost_util.Afgen.Afgen(cropparams['KDIFTB'])
        status.evapotranspiration.params.IAIRDU = cropparams['IAIRDU']
        status.evapotranspiration.params.IOX = cropparams['IOX']
        if hasattr(status,'soildata') and 'CRAIRC' in status.soildata:
            status.evapotranspiration.params.CRAIRC = status.soildata['CRAIRC']
        else:
            status.evapotranspiration.params.CRAIRC = 0

        if hasattr(status,'soildata') and 'SM0' in status.soildata:
            status.evapotranspiration.params.SM0 = status.soildata['SM0']
        if hasattr(status,'soildata') and 'SMW' in status.soildata:
            status.evapotranspiration.params.SMW = status.soildata['SMW']

        if hasattr(status,'soildata') and ((not 'NSL' in status.soildata) or status.soildata['NSL'] == 0):
            if 'SMFCF' in status.soildata:
                status.evapotranspiration.params.SMFCF = status.soildata['SMFCF']
                status.states.SM = status.soildata['SMFCF'] #initialize soil mositure to SMFCF
            else:
                raise Exception('Missing required variable SMFCF in soil data')
        else:
            if  hasattr(status, 'soildata'):
                if 'NSL' in status.soildata:
                    for il in range(0, status.soildata['NSL']):
                        status.soildata['SOIL_LAYERS'][il].SM = status.soildata['SOIL_LAYERS'][il].SMFCF
                else:
                    raise Exception('Missing required variable NSL in soil data')


        return status

    def integrate(self, status):
        return status

    def initialize(self, status):

        # helper variable for Counting days since oxygen stress (DSOS)
        # and total days with water and oxygen stress (IDWST, IDOST)
        status.rates.WaterStressReductionFactor = 1
        status.rates.TRA = 1
        status.rates.TRAMX = 1
        status.rates.EVWMX = 0
        status.rates.EVSMX = 0
        status.states._DSOS = 0 # number of days with shortage of oxigen
        status.states._IDWST = 0
        status.states._IDOST = 0
        status.rates.TRALY = 0
        status.rates.IDWS = False
        status.rates.IDOS = False

        # Reduction factor for transpiration in case of water shortage
        status.rates.RFWS = 1
        # Reduction factor for transpiration in case of oxygen shortage
        status.rates.RFOS = 1

        return status

    def SWEAF(self, ET0, DEPNR):
        """Calculates the Soil Water Easily Available Fraction (SWEAF).

        :param ET0: The evapotranpiration from a reference crop.
        :param DEPNR: The crop dependency number.

        The fraction of easily available soil water between field capacity and wilting point is a function of the
        potential evapotranspiration rate (for a closed canopy) in cm/day, ET0, and the crop group number,
        DEPNR (from 1 (=drought-sensitive) to 5 (=drought-resistent)). The function SWEAF describes this relationship
        given in tabular form by Doorenbos & Kassam (1979) and by Van Keulen & Wolf (1986; p.108, table 20)
        http://edepot.wur.nl/168025.
        """
        A = 0.76
        B = 1.5
        #   curve for CGNR 5, and other curves at fixed distance below it
        sweaf = 1. / (A + B * ET0) - (5. - DEPNR) * 0.10

        #   Correction for lower curves (CGNR less than 3)
        if (DEPNR < 3.):
            sweaf += (ET0 - 0.6) / (DEPNR * (DEPNR + 3.))

        return limit(0.10, 0.95, sweaf)

    def IsWaterBalanceStarted(self, status):
        """
        return true if, according to the type of water balance start, the water balance is already started at the current day
        :param status:
        :return: true if started, false otherwise
        """
        if status.evapotranspiration.params.PerformWaterBalanceStartInAdvance:
            if status.POTENTIAL_WATER_STARTDATE_date is None:
                raise Exception(
                    "Error running evapotranspiration with option 'PerformWaterBalanceStartInAdvance': POTENTIAL_WATER_STARTDATE is None!")
            return status.POTENTIAL_WATER_STARTDATE_date <= status.day
        else:
            if status.evapotranspiration.params.PerformWaterBalanceStartInAdvanceUntilSowing:
                if status.POTENTIAL_WATER_STARTDATE_date is None:
                    raise Exception(
                        "Error running evapotranspiration with option 'PerformWaterBalanceStartInAdvance': POTENTIAL_WATER_STARTDATE is None!")
                return status.POTENTIAL_WATER_STARTDATE_date <= status.day
            else:
                return status.sowing_emergence_day <= status.day

    def runstep(self, status):
        p = status.evapotranspiration.params
        r = status.rates
        s = status.states

        # execute only after water balance calculation must be started
        if not self.IsWaterBalanceStarted(status):
            return status

        DVS = status.states.DVS
        LAI = status.states.LAI

        if status.states.NSL == 0:
            SM = status.states.SM

        KGLOB = 0.75 * p.KDIFTB(DVS)

        # crop specific correction on potential transpiration rate
        ET0 = p.CFET * status.states.ET0

        # maximum evaporation and transpiration rates
        EKL = round(exp(-KGLOB * LAI), 12)

        # co2 effect on potential traspiration
        if hasattr(status.evapotranspiration.params, 'Co2EffectOnPotentialTraspiration'):
            EKL *= float(status.evapotranspiration.params.Co2EffectOnPotentialTraspiration)

        r.EVWMX = status.states.E0 * EKL
        r.EVSMX = max(0., status.states.ES0 * EKL)
        r.TRAMX = max(0.000001, ET0 * (1. - EKL))

        # Critical soil moisture
        SWDEP = self.SWEAF(ET0, p.DEPNR)

        if status.states.NSL == 0:  # in case of unlayered soil, calculate the transpiration once
            SMCR = (1. - SWDEP) * (p.SMFCF - p.SMW) + p.SMW

            # Reduction factor for transpiration in case of water shortage (RFWS)
            status.rates.RFWS = limit(0., 1., (SM - p.SMW) / (SMCR - p.SMW))

            # reduction in transpiration in case of oxygen shortage (RFOS)
            # for non-rice crops, and possibly deficient land drainage
            if p.IAIRDU == 0 and p.IOX == 1:
                # critical soil moisture content for aeration
                SMAIR = p.SM0 - p.CRAIRC

                # count days since start oxygen shortage (up to num_days days)
                num_days = status.evapotranspiration.params.num_days_oxygen_shortage
                if SM >= SMAIR:
                    status.states._DSOS = min((status.states._DSOS + 1), num_days)
                else:
                    status.states._DSOS = 0

                # maximum reduction reached after num_days days
                RFOSMX = limit(0., 1., (p.SM0 - SM) / (p.SM0 - SMAIR))
                status.rates.RFOS = (RFOSMX + (1. - status.states._DSOS / num_days) * (1. - RFOSMX))  * (1-status.evapotranspiration.params.scaling_factor_oxygen_shortage)+status.evapotranspiration.params.scaling_factor_oxygen_shortage

            # For rice, or non-rice crops grown on well drained land
            elif p.IAIRDU == 1 or p.IOX == 0:
                status.rates.RFOS = 1.
            # Transpiration rate multiplied with reduction factors for oxygen and
            # water
            r.TRA = r.TRAMX * status.rates.RFOS * status.rates.RFWS


        else:  # in case of layered soil, calculate the transpiration for each layer
            if 'SOIL_LAYERS' in status.soildata:
                # calculation critical soil moisture content
                DEPTH = 0.0
                SUMTRA = 0.0

                TRALY = array.array('d', [0.0] * s.NSL)
                RFOSi = array.array('d', [0.0] * s.NSL)
                FRROOTi = array.array('d', [0.0] * s.NSL)
                for il in range(0, s.NSL):
                    SM0 = s.SOIL_LAYERS[il].SM0
                    SMW = s.SOIL_LAYERS[il].SMW
                    SMFCF = s.SOIL_LAYERS[il].SMFCF
                    CRAIRC = s.SOIL_LAYERS[il].CRAIRC

                    SMCR = (1. - SWDEP) * (SMFCF - SMW) + SMW
                    # reduction in transpiration in case of water shortage
                    status.rates.RFWS = limit(0., 1., (s.SOIL_LAYERS[il].SM - SMW) / (SMCR - SMW))

                    # reduction in transpiration in case of oxygen shortage. Boolean EnableWaterLogging should be set to true
                    # for non-rice crops, and possibly deficient land drainage
                    if (p.IAIRDU == 0 and p.IOX == 1 and hasattr(status.states,'EnableWaterLogging') and status.states.EnableWaterLogging):
                        num_days = status.evapotranspiration.params.num_days_oxygen_shortage
                        # critical soil moisture content for aeration
                        SMAIR = SM0 - CRAIRC
                        # count days since start oxygen shortage (up to num_days days)
                        if (s.SOIL_LAYERS[il].SM >= SMAIR): s._DSOS = min((s._DSOS + 1.), num_days)
                        if (s.SOIL_LAYERS[il].SM < SMAIR): s._DSOS = 0.
                        # maximum reduction reached after num_days days
                        RFOSMX = limit(0., 1., (SM0 - s.SOIL_LAYERS[il].SM) / (SM0 - SMAIR))
                        RFOSi[il] = (RFOSMX + (1. - s._DSOS / num_days) * (1. - RFOSMX)) * (1-status.evapotranspiration.params.scaling_factor_oxygen_shortage)+status.evapotranspiration.params.scaling_factor_oxygen_shortage

                    # for rice, or non-rice crops grown on perfectly drained land, or if the EnableWaterLogging flag is not True
                    else:
                        RFOSi[il] = 1.

                    if status.evapotranspiration.params.USE_HERMES_FRROOT:
                        # davidefuma 28-02-2022 multiply FRROOT per the factor of distribution of roots calculated by hermes root depth
                        FRROOTi[il] = status.hermesrootdepth.hermes_roots_layer_data[il].percentageOfRootInLayer / 100
                    else:  # original FRROOT based on ration between layer depth and root depth
                        if s.RD > 0:
                            FRROOTi[il] = max(0.0, (min(s.RD, DEPTH + s.SOIL_LAYERS[il].TSL) - DEPTH)) / s.RD
                        else:
                            FRROOTi[il] = 1

                    TRALY[il] = status.rates.RFWS * RFOSi[il] * r.TRAMX * FRROOTi[il]
                    DEPTH += s.SOIL_LAYERS[il].TSL

                r.TRA = sum(TRALY)
                r.TRA = min(r.TRA, r.TRAMX) #forced than TRA should be <= TRAMX
                r.TRALY = TRALY
                # r.TRA=r.TRAMX #TODO:eliminazione water stress!! Nel funzionamento normale, commentare questa riga!
                r.WaterStressReductionFactor = r.TRA / r.TRAMX
                status.rates.RFOS = 0
                if s.RD > 0:
                    for il in range(0, s.NSL):
                        status.rates.RFOS += RFOSi[il] * FRROOTi[il]
                else:
                    status.rates.RFOS = 1

            else:
                status.rates.RFOS = 1.
        # Counting stress days
        # counting water stress days. Condition for a day to be considered a stress day is: RFWS < 1
        if status.rates.RFWS < 1.:
            r.IDWS = True
            status.states._IDWST += 1

        #counting oxygen stress days. Condition for a day to be considered a stress day is: round(RFOS,3) < 1
        if round(status.rates.RFOS,3) < 1.:
            r.IDOS = True
            status.states._IDOST += 1

        return status


    def getinputslist(self):
        return {
            "soildata": {"Description": "Soil data input", "Type": "Dictionary", "UnitOfMeasure": "-",
                         "StatusVariable": "status.soildata"},
            "SOIL_LAYERS": {"Description": "Soil layers data (only in case of multi layer soil data)", "Type": "List",
                            "UnitOfMeasure": "-",
                            "StatusVariable": "status.states.SOIL_LAYERS"},

            "NSL": {"Description": "Number of soil layers (only in case of multi layer soil data)", "Type": "Number",
                    "UnitOfMeasure": "-",
                    "StatusVariable": "status.states.NSL"},
            "day": {"Description": "Current day", "Type": "Number", "UnitOfMeasure": "doy",
                    "StatusVariable": "status.day"},
            "sowing_emergence_day": {"Description": "Doy of sowing or emergence", "Type": "Number",
                                     "UnitOfMeasure": "doy",
                                     "StatusVariable": "status.sowing_emergence_day"},
            "POTENTIAL_WATER_STARTDATE_date": {"Description": "Doy of start of water balance calculation", "Type": "Number",
                                     "UnitOfMeasure": "doy",
                                     "StatusVariable": "status.POTENTIAL_WATER_STARTDATE_date"},

            "DVS": {"Description": "Development stage", "Type": "Number", "UnitOfMeasure": "unitless",
                    "StatusVariable": "status.states.DVS"},
            "LAI": {"Description": "Leaf area index",
                    "Type": "Number", "UnitOfMeasure": "unitless",
                    "StatusVariable": "status.states.LAI"},
            "SM": {"Description": "Actual volumetric soil moisture content",
                    "Type": "Number", "UnitOfMeasure": "",
                    "StatusVariable": "status.states.SM"},
            "E0": {"Description": "Open water evapotranspiration",
                   "Type": "Number", "UnitOfMeasure": "cm",
                   "StatusVariable": "status.states.E0"},
            "ES0": {"Description": "Bare soil evapotranspiration",
                    "Type": "Number", "UnitOfMeasure": "cm",
                    "StatusVariable": "status.states.ES0"},
            "ET0": {"Description": "Canopy evapotranspiration",
                    "Type": "Number", "UnitOfMeasure": "cm",
                    "StatusVariable": "status.states.ET0"},
            "RD": {"Description": "Root depth", "Type": "Number", "UnitOfMeasure": "cm",
                   "StatusVariable": "status.states.RD"},
            "_DSOS": {"Description": "Number of days with shortage of oxygen", "Type": "Number", "UnitOfMeasure": "days",
                   "StatusVariable": "status.states._DSOS"},
        }


    def getoutputslist(self):
        return {
            "SOIL_LAYERS": {"Description": "Soil layers data (only in case of multi layer soil data)", "Type": "List",
                            "UnitOfMeasure": "-",
                            "StatusVariable": "status.states.SOIL_LAYERS"},
            "_DSOS": {"Description": "Number of days with shortage of oxygen", "Type": "Number", "UnitOfMeasure": "days",
                      "StatusVariable": "status.states._DSOS"},
            "TRA": {"Description": "Actual transpiration rate from the plant canopy", "Type": "Number",
                    "UnitOfMeasure": "cm/day",
                    "StatusVariable": "status.rates.TRA"},
            "TRALY": {"Description": "Array of actual transpiration rates of different layers (one value per layer, only in case of multi layer soil model)", "Type": "ArrayOfNumbers",
                    "UnitOfMeasure": "cm/day",
                    "StatusVariable": "status.rates.TRALY"},
            "TRAMX": {"Description": "Max transpiration rate from the plant canopy", "Type": "Number",
                      "UnitOfMeasure": "cm/day",
                      "StatusVariable": "status.rates.TRAMX"},
            "EVWMX": {"Description": "Maximum evaporation rate from an open water surface", "Type": "Number",
                      "UnitOfMeasure": "cm/day",
                      "StatusVariable": "status.rates.EVWMX"},
            "EVSMX": {"Description": "Maximum evaporation rate from a wet soil surface", "Type": "Number",
                      "UnitOfMeasure": "cm/day",
                      "StatusVariable": "status.rates.EVSMX"},
            "RFWS": {"Description": "Reduction factor for transpiration in case of water shortage ", "Type": "Number",
                      "UnitOfMeasure": "unitless",
                      "StatusVariable": "status.rates.RFWS"},
            "WaterStressReductionFactor": {"Description": "Reduction factor for water stress calculated as TRA/TRAMX", "Type": "Number",
                     "UnitOfMeasure": "unitless",
                     "StatusVariable": "status.rates.WaterStressReductionFactor"},

            "IDWS": {"Description": "Indicates water stress on this day (True|False) ", "Type": "Boolean",
                     "UnitOfMeasure": "unitless",
                     "StatusVariable": "status.rates.IDWS"},
            "IDOS": {"Description": "Indicates oxygen stress on this day (True|False)  ",
                     "Type": "Boolean",
                     "UnitOfMeasure": "unitless",
                     "StatusVariable": "status.rates.IDOS"},
            "_IDWST": {"Description": "Sum of water stress days", "Type": "Number",
                     "UnitOfMeasure": "days",
                     "StatusVariable": "status.states._IDWST"},
            "_IDOST": {"Description": "Sum of oxygen stress days",
                     "Type": "Number",
                     "UnitOfMeasure": "days",
                     "StatusVariable": "status.states._IDOST"},

        }
