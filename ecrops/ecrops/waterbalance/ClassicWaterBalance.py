# -*- coding: utf-8 -*-
# This component is derived from PCSE software/Wofost model
# (Copyright @ 2004-2014 Alterra, Wageningen-UR; Allard de Wit allard.dewit@wur.nl, April 2014)
# and modified by EC-JRC for the eCrops framework under the European Union Public License (EUPL), Version 1.2
# European Commission, Joint Research Centre, March 2023


from math import sqrt

from ecrops.wofost_util.util import limit

from ecrops.Printable import Printable

from ecrops.wofost_util import Afgen

RootDepthForWaterbalanceInAdvance = 10 #10 cm

class WaterbalanceFD:
    """Classic mono layer water balance for freely draining soils under water-limited production.

    The purpose of the soil water balance calculations is to estimate the
    daily value of the soil moisture content. The soil moisture content
    influences soil moisture uptake and crop transpiration.

    The dynamic calculations are carried out in two sections, one for the
    calculation of rates of change per timestep (= 1 day) and one for the
    calculation of summation variables and state variables. The water balance
    is driven by rainfall, possibly buffered as surface storage, and
    evapotranspiration. The processes considered are infiltration, soil water
    retention, percolation (here conceived as downward water flow from rooted
    zone to second layer), and the loss of water beyond the maximum root zone.

    The textural profile of the soil is conceived as homogeneous. Initially the
    soil profile consists of two layers, the actually rooted  soil and the soil
    immediately below the rooted zone until the maximum rooting depth (soil and
    crop dependent). The extension of the root zone from initial rooting depth
    to maximum rooting depth is described in Root_Dynamics class. From the
    moment that the maximum rooting depth is reached the soil profile is
    described as a one layer system. The class WaterbalanceFD is derived
    from WATFD.FOR in WOFOST7.1

    **Simulation parameters:** (provide in crop, soil and sitedata dictionary)

    ======== =============================================== =======  ==========
     Name     Description                                     Type     Unit
    ======== =============================================== =======  ==========
    SMFCF     Field capacity of the soil                       SSo     -
    SM0       Porosity of the soil                             SSo     -
    SMW       Wilting point of the soil                        SSo     -
    CRAIRC    Soil critical air content (waterlogging)         SSo     -
    SOPE      maximum percolation rate root zone               SSo    |cmday-1|
    KSUB      maximum percolation rate subsoil                 SSo    |cmday-1|
    K0        hydraulic conductivity of saturated soil         SSo    |cmday-1|
    RDMSOL    Soil rootable depth                              SSo     cm
    IFUNRN    Indicates whether non-infiltrating fraction of   SSi    -
              rain is a function of storm size (1)
              or not (0)
    SSMAX     Maximum surface storage                          SSi     cm
    SSI       Initial surface storage                          SSi     cm
    WAV       Initial amount of water in total soil            SSi     cm
              profile
    NOTINF    Maximum fraction of rain not-infiltrating into   SSi     -
              the soil
    SMLIM     Initial maximum moisture content in initial      SSi     -
              rooting depth zone.
    IAIRDU    Switch airducts on (1) or off (0)                SCr     -
    RDMCR     Maximum rooting depth of the crop                SCr      cm
    RDI       Initial rooting depth of the crop                SCr      cm
    ======== =============================================== =======  ==========

    **State variables:**

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    SM        Volumetric moisture content in root zone          Y    -
    SS        Surface storage (layer of water on surface)       N    cm
    W         Amount of water in root zone                      N    cm
    WI        Initial amount of water in the root zone          N    cm
    WLOW      Amount of water in the subsoil (between current   N    cm
              rooting depth and maximum rootable depth)
    WLOWI     Initial amount of water in the subsoil                 cm
    WWLOW     Total amount of water in the  soil profile        N    cm
              WWLOW = WLOW + W
    WTRAT     Total water lost as transpiration as calculated   N    cm
              by the water balance. This can be different
              from the CTRAT variable which only counts
              transpiration for a crop cycle.
    EVST      Total evaporation from the soil surface           N    cm
    EVWT      Total evaporation from a water surface            N    cm
    TSR       Total surface runoff                              N    cm
    RAINT     Total amount of rainfall                          N    cm
    WDRT      Amount of water added to root zone by increase    N    cm
              of root growth
    TOTINF    Total amount of infiltration                      N    cm
    TOTIRR    Total amount of effective irrigation              N    cm
    PERCT     Total amount of water percolating from rooted     N    cm
              zone to subsoil
    LOSST     Total amount of water lost to deeper soil         N    cm
    WBALRT    Checksum for root zone waterbalance. Will be      N    cm
              calculated within `finalize()`, abs(WBALRT) >
              0.0001 will raise a WaterBalanceError
    WBALTT    Checksum for total waterbalance. Will be          N    cm
              calculated within `finalize()`, abs(WBALTT) >
              0.0001 will raise a WaterBalanceError
    =======  ================================================= ==== ============

    **Rate variables:**

    ======== ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    ======== ================================================= ==== ============
    EVS      Actual evaporation rate from soil                  N    |cmday-1|
    EVW      Actual evaporation rate from water surface         N    |cmday-1|
    WTRA     Actual transpiration rate from plant canopy,       N    |cmday-1|
             is directly derived from the variable "TRA" in
             the evapotranspiration module
    RAIN     Rainfall rate for current day                      N    |cmday-1|
    RIN      Infiltration rate for current day                  N    |cmday-1|
    RIRR     Effective irrigation rate for current day,         N    |cmday-1|
             computed as irrigation amount * efficiency.
    PERC     Percolation rate to non-rooted zone                N    |cmday-1|
    LOSS     Rate of water loss to deeper soil                  N    |cmday-1|
    DW       Change in amount of water in rooted zone as a      N    |cmday-1|
             result of infiltration, transpiration and
             evaporation.
    DWLOW    Change in amount of water in subsoil               N    |cmday-1|
    ======== ================================================= ==== ============


    **External dependencies:**

    ============ ============================== ====================== =========
     Name        Description                         Provided by         Unit
    ============ ============================== ====================== =========
     TRA          Crop transpiration rate       Evapotranspiration     |cmday-1|
     EVSMX        Maximum evaporation rate      Evapotranspiration     |cmday-1|
                  from a soil surface below
                  the crop canopy
     EVWMX        Maximum evaporation rate       Evapotranspiration    |cmday-1|
                  from a water surface below
                  the crop canopy
     RD           Rooting depth                  Root_dynamics          cm
    ============ ============================== ====================== =========


    A Waterbalance warning is printed in std output when the waterbalance is not closing at the
    end of the simulation cycle (e.g water has "leaked" away).
    """

    def getparameterslist(self):
        return {
            "RDMSOL": {"Description": "Soil rootable depth", "Type": "Number", "Mandatory": "True",  "UnitOfMeasure": "cm"},
            "WAV": {"Description": "Initial amount of water in total soil in profile", "Type": "Number", "Mandatory": "True",
                     "UnitOfMeasure": "cm"},
            "SSI": {"Description": "Initial surface storage", "Type": "Number", "Mandatory": "True",
                     "UnitOfMeasure": "cm"},
            "SMW": {"Description": "Volumetric soil moisture content at wilting point", "Type": "Number", "Mandatory": "True",
                      "UnitOfMeasure": "unitless"},
            "SMFCF": {"Description": "Volumetric soil moisture content at field capacity", "Type": "Number", "Mandatory": "True",
                      "UnitOfMeasure": "unitless"},
            "SM0": {"Description": "Porosity of the soil", "Type": "Number", "Mandatory": "True",
                      "UnitOfMeasure": "unitless"},
            "SSMAX": {"Description": "Maximum surface storage", "Type": "Number", "Mandatory": "True",
                      "UnitOfMeasure": "unitless"},
            "IFUNRN": {"Description": "Indicates whether non-infiltrating fraction of rain is a function of storm size (1) or not (0)", "Type": "Number", "Mandatory": "True",
                      "UnitOfMeasure": "unitless"},
            "NOTINF": {"Description": "Maximum fraction of rain not-infiltrating into the soil", "Type": "Number", "Mandatory": "True",
                      "UnitOfMeasure": "unitless"},
            "SOPE": {"Description": "Maximum percolation rate root zone", "Type": "Number", "Mandatory": "True",
                      "UnitOfMeasure": "cm/day"},
            "KSUB": {"Description": "Maximum percolation rate subsoil", "Type": "Number", "Mandatory": "True",
                      "UnitOfMeasure": "cm/day"}
        }

    def setparameters(self, status):



        status.classicwaterbalance = Printable()
        status.classicwaterbalance.states = Printable()
        status.classicwaterbalance.rates = Printable()
        status.soildata = Printable()
        status.soildata = status.soilparameters
        status.classicwaterbalance.params = Printable()
        status.classicwaterbalance.params.RDMSOL = status.soildata['RDMSOL']
        status.classicwaterbalance.params.PerformWaterBalanceStartInAdvance = 'CALC_SOILWATER_BEFORE_SOWING' in status.allparameters and status.allparameters[
            'CALC_SOILWATER_BEFORE_SOWING']==1
        if status.classicwaterbalance.params.PerformWaterBalanceStartInAdvance == False:
            # in case of soil water from sowing, the soil initial water is given by WAV
            status.classicwaterbalance.params.WAV = status.soildata['WAV']
        else:
            #in case of soil water in advance, the soil initial water is given by ROOTING_DEPTH_POT_WATER_ISV
            status.classicwaterbalance.params.WAV = status.soildata['ROOTING_DEPTH_POT_WATER_ISV']
        status.classicwaterbalance.params.SSI = status.soildata['SSI']
        status.classicwaterbalance.params.SMW = status.soildata['SMW']
        status.classicwaterbalance.params.SMFCF = status.soildata['SMFCF']
        status.classicwaterbalance.params.SM0 = status.soildata['SM0']
        status.classicwaterbalance.params.SSMAX = status.soildata['SSMAX']
        status.classicwaterbalance.params.IFUNRN = status.soildata['IFUNRN']
        status.classicwaterbalance.params.NOTINF = status.soildata['NOTINF']
        status.classicwaterbalance.params.SOPE = status.soildata['SOPE']
        status.classicwaterbalance.params.KSUB = status.soildata['KSUB']


        return status

    def initialize(self,status):



        # previous and maximum rooting depth value
        status.classicwaterbalance.states.RDold = float(-99.)
        status.classicwaterbalance.states.RDM = float(-99.)
        # Counter for Days-Dince-Last-Rain
        status.classicwaterbalance.states.DSLR = float(-99.)
        # Infiltration rate of previous day
        status.classicwaterbalance.states.RINold = float(-99)
        # Fraction of non-infiltrating rainfall as function of storm size
        status.classicwaterbalance.states.NINFTB = Afgen.Afgen([])
        # Flag indicating crop present or not
        status.classicwaterbalance.states.in_crop_cycle = False
        # Flag indicating that a crop was removed and therefore the thickness
        # of the rootzone shift back to its initial value (params.RDI)
        status.classicwaterbalance.states.rooted_layer_needs_reset = False
        # placeholder for irrigation
        status.classicwaterbalance.states._RIRR = float(0.)

        # Assign parameter values
        p = status.classicwaterbalance.params
        s = status.classicwaterbalance.states
        r = status.classicwaterbalance.rates

        # Current, maximum and old rooting depth
        s.RD = s.RDI
        s.RDM = max(s.RDI, min(p.RDMSOL, s.RDMCR))
        s.RDold = s.RD


        # Initial surface storage
        s.SS = p.SSI

        # Initial soil moisture content and amount of water in rooted zone,
        # limited by SMLIM. Save initial value (WI)
        s.SM = limit(p.SMW, p.SMFCF, (p.SMW + p.WAV / s.RD))
        s.SMUR = 0
        s.W = s.SM * s.RD
        s.WI = s.W

        # initial amount of soil moisture between current root zone and maximum
        # rootable depth (WLOW). Save initial value (WLOWI)
        s.WLOW = limit(0., p.SM0 * (s.RDM - s.RD), (p.WAV + s.RDM * p.SMW - s.W))
        s.WLOWI = s.WLOW

        # Total water depth in soil column (root zone + subsoil)
        s.WWLOW = s.W + s.WLOW

        # soil evaporation, days since last rain (DLSR) set to 1
        s.DSLR = 1.
        if status.classicwaterbalance.params.PerformWaterBalanceStartInAdvance:
            #initialize days since last rain (DLSR) set to 1 if the soil is wetter then halfway between SMW and SMFCF, else DSLR=5.
            if s.SM < p.SMW + 0.5 * (p.SMFCF - p.SMW):
                s.DSLR = 5.

        # Initialize some remaining helper variables
        s.RINold = 0.
        #self.in_crop_cycle = False
        s.NINFTB =  Afgen.Afgen([0.0, 0.0, 0.5, 0.0, 1.5, 1.0])


        #initialize the states to zero
        s.WTRAT = 0.
        s.EVST = 0.
        s.EVWT = 0.
        s.TSR = 0.
        s.RAINT=0.
        s.WDRT=0.
        s.TOTINF=0.
        s.TOTIRR=0.
        s.PERCT=0.
        s.LOSST=0.
        s.WBALRT=-999.
        s.WBALTT=-999.

        #initialize the rates to zero
        r.WTRA=0
        r.EVW=0
        r.EVS=0
        r.RAIN=0
        r.RIRR=0
        r.RIN=0
        r.DW=0
        r.DWLOW=0
        r.PERC=0
        r.LOSS=0





        return status



    def runstep(self, status):
        s = status.classicwaterbalance.states
        p = status.classicwaterbalance.params
        r = status.classicwaterbalance.rates

        if status.classicwaterbalance.params.PerformWaterBalanceStartInAdvance == False:
            # start calculating the water balance only after emergence
            if s.DOE is None or (status.day - s.DOE).days < 0:
                return status
        else:
            # start calculating the water balance only after POTENTIAL_WATER_STARTDATE
            if (status.day - status.POTENTIAL_WATER_STARTDATE_date).days < 0 :
                return status
            # during the period to calculated water balance in advance
            if (status.day - status.POTENTIAL_WATER_STARTDATE_date).days <= 90:
                s.RD = RootDepthForWaterbalanceInAdvance
            #at the end of the period to calculated water balance in advance
            if (status.day - status.POTENTIAL_WATER_STARTDATE_date).days == 90: #this period takes 90 days
                #redistribute the current water between root depth and below root depth
                currentSoilWater = s.SM * RootDepthForWaterbalanceInAdvance + s.SMUR * (s.RDM-RootDepthForWaterbalanceInAdvance)
                calculatedWAV = currentSoilWater - p.SMW  * s.RDM
                s.SM = limit(p.SMW, p.SMFCF, (p.SMW + calculatedWAV / s.RD))
                s.W = s.SM * s.RD
                initialWaterContentUnrooted_WLOWI = max(0,min(p.SM0 * (s.RDM-s.RD),calculatedWAV+(s.RDM*p.SMW)-s.W))

                s.WLOW = initialWaterContentUnrooted_WLOWI
                s.SMUR = s.WLOW / (s.RDM - s.RD)

                # at the end of the period in advance, reset the cumulated outputs (LossToSubSoil,SoilEvaporation,RootWaterUptakeCum), so that they represent only the real crop period
                s.WTRAT = 0
                s.LOSST = 0
                s.PERCT =0
                s.EVWT=0
                s.EVST = 0
                s.RAINT = 0
                s.TOTINF = 0
                s.TOTIRR = 0


        # Rate of irrigation (RIRR)
        r.RIRR = 0.

        # calculation of new amount of soil moisture in rootzone by root growth
        RD = s.RD
        if (RD - s.RDold) > 0.001:
            # water added to root zone by root growth, in cm
            WDR = s.WLOW * (RD - s.RDold) / (s.RDM - s.RDold)
            s.WLOW -= WDR

            # total water addition to rootzone by root growth
            s.WDRT += WDR
            # amount of soil moisture in extended rootzone
            s.W += WDR

        # Rainfall rate


        # Transpiration and maximum soil and surface water evaporation rates
        # are calculated by the crop Evapotranspiration module.
        # However, if the crop is not yet emerged then set TRA=0 and use
        # the potential soil/water evaporation rates directly because there is
        # no shading by the canopy.
        if r.TRA == 100:
            r.WTRA = 0.
            EVWMX = r.E0
            EVSMX = r.ES0
        else:
            r.WTRA = r.TRA
            EVWMX = r.EVWMX
            EVSMX = r.EVSMX

        # Actual evaporation rates
        r.EVW = 0.
        r.EVS = 0.
        if s.SS > 1.:
            # If surface storage > 1cm then evaporate from water layer on
            # soil surface
            r.EVW = EVWMX
        else:
            # else assume evaporation from soil surface
            if s.RINold >= 1:
                # If infiltration >= 1cm on previous day assume maximum soil
                # evaporation
                r.EVS = EVSMX
                s.DSLR = 1.
            else:
                # Else soil evaporation is a function days-since-last-rain (DSLR)
                s.DSLR += 1
                EVSMXT = EVSMX * (sqrt(s.DSLR) - sqrt(s.DSLR - 1))
                EVS = min(EVSMX, EVSMXT + s.RINold)
                r.EVS = min(EVS, s.W)

        # Preliminary infiltration rate (RINPRE)
        if s.SS < 0.1:
            # without surface storage
            if (p.IFUNRN == 0):
                RINPRE = (1. - p.NOTINF) * r.RAIN + r.RIRR + s.SS

            else:
                RINPRE = (1. - p.NOTINF * s.NINFTB(r.RAIN)) * r.RAIN + \
                         r.RIRR + s.SS
        else:
            # with surface storage, infiltration limited by SOPE
            AVAIL = s.SS + (r.RAIN * (1. - p.NOTINF)) + r.RIRR - r.EVW
            RINPRE = min(p.SOPE, AVAIL)

        RD = s.RD

        # equilibrium amount of soil moisture in rooted zone
        WE = p.SMFCF * RD
        # percolation from rooted zone to subsoil equals amount of
        # excess moisture in rooted zone, not to exceed maximum percolation rate
        # of root zone (SOPE)
        PERC1 = limit(0., p.SOPE, (s.W - WE) - r.WTRA - r.EVS)

        # loss of water at the lower end of the maximum root zone
        # equilibrium amount of soil moisture below rooted zone
        WELOW = p.SMFCF * (s.RDM - RD)
        LOSS = limit(0., p.KSUB, (s.WLOW - WELOW + PERC1))

        r.LOSS = LOSS

        # percolation not to exceed uptake capacity of subsoil
        PERC2 = ((s.RDM - RD) * p.SM0 - s.WLOW) + LOSS
        r.PERC = min(PERC1, PERC2)

        # adjustment of infiltration rate
        r.RIN = min(RINPRE, (p.SM0 - s.SM) * RD + r.WTRA + r.EVS + r.PERC)
        s.RINold = r.RIN

        # rates of change in amounts of moisture W and WLOW
        r.DW = r.RIN - r.WTRA - r.EVS - r.PERC
        r.DWLOW = r.PERC - r.LOSS


        #integrate
        if status.classicwaterbalance.params.PerformWaterBalanceStartInAdvance == False:
            # start calculating the water balance only after emergence
            if s.DOE is None or (status.day - s.DOE).days < 0:
                return status
        else:
            # start calculating the water balance only after POTENTIAL_WATER_STARTDATE
            if (status.day - status.POTENTIAL_WATER_STARTDATE_date).days < 0:
                return status

        # INTEGRALS OF THE WATERBALANCE: SUMMATIONS AND STATE VARIABLES
        # total transpiration
        s.WTRAT += r.WTRA

        # total evaporation from surface water layer and/or soil
        s.EVWT += r.EVW
        s.EVST += r.EVS

        # totals for rainfall, irrigation and infiltration
        s.RAINT += r.RAIN
        s.TOTINF += r.RIN
        s.TOTIRR += r.RIRR

        # Update surface storage, any storage > SSMAX goes to total surface
        # runoff (TSR)
        SSPRE = s.SS + (r.RAIN + r.RIRR - r.EVW - r.RIN)
        s.SS = min(SSPRE, p.SSMAX)
        s.TSR += (SSPRE - s.SS)

        # amount of water in rooted zone
        W_NEW = s.W + r.DW
        if (W_NEW < 0.0):
            # If negative soil water depth, set W to zero and subtract W_NEW
            # from total soil evaporation to keep the balance.
            # Note: W_NEW is negative here!!
            s.EVST += W_NEW
            s.W = 0.0
        else:
            s.W = W_NEW

        # total percolation and loss of water by deep leaching
        s.PERCT += r.PERC
        s.LOSST += r.LOSS

        # amount of water in unrooted, lower part of rootable zone
        s.WLOW += r.DWLOW
        # total amount of water in the whole rootable zone
        s.WWLOW = s.W + s.WLOW

        # CHANGE OF ROOTZONE SUBSYSTEM BOUNDARY

        # Redefine the rootzone when the crop is finished. As a result there
        # no roots anymore (variable RD) and the rootzone shifts back to its
        # initial depth (params.RDI). As a result the amount of water in the
        # initial rooting depth and the unrooted layer must be redistributed.
        # Note that his is a rather artificial solution resulting from the fact
        # that the rooting depth is user as to define a layer in the WOFOST
        # water balance.
        if s.rooted_layer_needs_reset is True:
            status = self._reset_rootzone(status)



        # mean soil moisture content in rooted zone
        s.SM = s.W / RD
        if s.RDM == RD:
            s.SMUR = 0
        else:
            s.SMUR = s.WLOW / (s.RDM - RD)
        # save rooting depth
        s.RDold = RD

        # Checksums waterbalance for systems without groundwater
        # for rootzone (WBALRT) and whole system (WBALTT)
        s.WBALRT = s.TOTINF + s.WI + s.WDRT - s.EVST - s.WTRAT - s.PERCT - s.W
        s.WBALTT = (p.SSI + s.RAINT + s.TOTIRR + s.WI - s.W + s.WLOWI -
                    s.WLOW - s.WTRAT - s.EVWT - s.EVST - s.TSR - s.LOSST - s.SS)
        if abs(s.WBALRT) > 0.0001:
            msg = "Water balance for root zone does not close."
            # raise Exception(msg)

        if abs(s.WBALTT) > 0.0001:
            msg = "Water balance for complete soil profile does not close.\n"
            msg += ("Total INIT + IN:   %f\n" % (s.WI + s.WLOWI + p.SSI + s.TOTIRR +
                                                 s.RAINT))
            msg += ("Total FINAL + OUT: %f\n" % (s.W + s.WLOW + s.SS + s.EVWT + s.EVST +
                                                 s.WTRAT + s.TSR + s.LOSST))
            # raise Exception(msg)


        return status

    def integrate(self,status):
        s = status.classicwaterbalance.states
        p = status.classicwaterbalance.params
        r = status.classicwaterbalance.rates



        return status



    def _reset_rootzone(self,status):

        p = status.classicwaterbalance.params
        s=status.classicwaterbalance.states

        s.rooted_layer_needs_reset = False

        # water added to the subsoil by root zone reset
        WDR = s.W * (status.RDold - s.RDI) / (status.RDold)
        s.WLOW += WDR

        # total water subtracted from, rootzone by root zone reset
        s.WDRT -= WDR
        # amount of soil moisture in new resetted rootzone
        s.W -= WDR
        return status
