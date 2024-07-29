# -*- coding: utf-8 -*-
# This component is derived from PCSE software/Wofost model
# (Copyright @ 2004-2014 Alterra, Wageningen-UR; Allard de Wit allard.dewit@wur.nl, April 2014)
# and modified by EC-JRC for the eCrops framework under the European Union Public License (EUPL), Version 1.2
# European Commission, Joint Research Centre, March 2023

from math import cos, sqrt, exp
from math import pi

import ecrops.wofost_util.Afgen
from ..Printable import Printable
from collections import deque
from ecrops.Step import Step

def totass(DAYL, AMAX, EFF, LAI, KDIF, AVRAD, DIFPP, DSINBE, SINLD, COSLD):
    """ This routine calculates the daily total gross CO2 assimilation by performing a Gaussian integration over
    time. At three different times of the day, irradiance is computed and used to calculate the instantaneous
    canopy assimilation, whereafter integration takes place. More information on this routine is given by Spitters et
    al. (1988).

    FORMAL PARAMETERS:  (I=input,O=output,C=control,IN=init,T=time)
    name   type meaning                                    units  class
    ----   ---- -------                                    -----  -----
    DAYL    R4  Astronomical daylength (base = 0 degrees)     h      I
    AMAX    R4  Assimilation rate at light saturation      kg CO2/   I
                                                          ha leaf/h
    EFF     R4  Initial light use efficiency              kg CO2/J/  I
                                                          ha/h m2 s
    LAI     R4  Leaf area index                             ha/ha    I
    KDIF    R4  Extinction coefficient for diffuse light             I
    AVRAD   R4  Daily shortwave radiation                  J m-2 d-1 I
    DIFPP   R4  Diffuse irradiation perpendicular to direction of
                light                                      J m-2 s-1 I
    DSINBE  R4  Daily total of effective solar height         s      I
    SINLD   R4  Seasonal offset of sine of solar height       -      I
    COSLD   R4  Amplitude of sine of solar height             -      I
    DTGA    R4  Daily total gross assimilation           kg CO2/ha/d O

    Authors: Daniel van Kraalingen
    Date   : April 1991

    Python version:
    Authors: Allard de Wit
    Date   : September 2011
    """

    # Gauss points and weights
    XGAUSS = [0.1127017, 0.5000000, 0.8872983]
    WGAUSS = [0.2777778, 0.4444444, 0.2777778]

    # calculation of assimilation is done only when it will not be zero
    # (AMAX >0, LAI >0, DAYL >0)
    DTGA = 0.
    if (AMAX > 0. and LAI > 0. and DAYL > 0.):
        for i in range(3):
            HOUR = 12.0 + 0.5 * DAYL * XGAUSS[i]
            SINB = max(0., SINLD + COSLD * cos(2. * pi * (HOUR + 12.) / 24.))
            PAR = 0.5 * AVRAD * SINB * (1. + 0.4 * SINB) / DSINBE
            PARDIF = min(PAR, SINB * DIFPP)
            PARDIR = PAR - PARDIF
            FGROS = assim(AMAX, EFF, LAI, KDIF, SINB, PARDIR, PARDIF)
            DTGA += FGROS * WGAUSS[i]
    DTGA *= DAYL

    return DTGA


def assim(AMAX, EFF, LAI, KDIF, SINB, PARDIR, PARDIF):
    """This routine calculates the gross CO2 assimilation rate of the whole crop, FGROS, by performing a Gaussian
    integration over depth in the crop canopy. At three different depths in the canopy, i.e. for different values of
    LAI, the assimilation rate is computed for given fluxes of photosynthetically active radiation, whereafter
    integration over depth takes place. More information on this routine is given by Spitters et al. (1988). The
    input variables SINB, PARDIR and PARDIF are calculated in routine TOTASS. Subroutines and functions called: none.
    Called by routine TOTASS.

    Author: D.W.G. van Kraalingen, 1986

    Python version:
    Allard de Wit, 2011
    """
    # Gauss points and weights
    XGAUSS = [0.1127017, 0.5000000, 0.8872983]
    WGAUSS = [0.2777778, 0.4444444, 0.2777778]

    SCV = 0.2

    # 13.2 extinction coefficients KDIF, KDIRBL, KDIRT
    REFH = (1. - sqrt(1. - SCV)) / (1. + sqrt(1. - SCV))
    REFS = REFH * 2. / (1. + 1.6 * SINB)
    KDIRBL = (0.5 / SINB) * KDIF / (0.8 * sqrt(1. - SCV))
    KDIRT = KDIRBL * sqrt(1. - SCV)

    # 13.3 three-point Gaussian integration over LAI
    FGROS = 0.
    for i in range(3):
        LAIC = LAI * XGAUSS[i]
        # absorbed diffuse radiation (VISDF),light from direct
        # origine (VIST) and direct light (VISD)
        VISDF = (1. - REFS) * PARDIF * KDIF * exp(-KDIF * LAIC)
        VIST = (1. - REFS) * PARDIR * KDIRT * exp(-KDIRT * LAIC)
        VISD = (1. - SCV) * PARDIR * KDIRBL * exp(-KDIRBL * LAIC)

        # absorbed flux in W/m2 for shaded leaves and assimilation
        VISSHD = VISDF + VIST - VISD
        FGRSH = AMAX * (1. - exp(-VISSHD * EFF / max(2.0, AMAX)))

        # direct light absorbed by leaves perpendicular on direct
        # beam and assimilation of sunlit leaf area
        VISPP = (1. - SCV) * PARDIR / SINB
        if (VISPP <= 0.):
            FGRSUN = FGRSH
        else:
            FGRSUN = AMAX * (1. - (AMAX - FGRSH) \
                             * (1. - exp(-VISPP * EFF / max(2.0, AMAX))) / (EFF * VISPP))

        # fraction of sunlit leaf area (FSLLA) and local
        # assimilation rate (FGL)
        FSLLA = exp(-KDIRBL * LAIC)
        FGL = FSLLA * FGRSUN + (1. - FSLLA) * FGRSH

        # integration
        FGROS += FGL * WGAUSS[i]

    FGROS = FGROS * LAI
    return FGROS


class WOFOST_Assimilation(Step):
    """This step implements a WOFOST/SUCROS style assimilation routine.

    WOFOST calculates the daily gross CO2 assimilation rate of a crop from the absorbed radiation and the
    photosynthesis-light response curve of individual leaves. This response is dependent on temperature and leaf age.
    The absorbed radiation is calculated from the total incoming radiation and the leaf area. Daily gross CO2
    assimilation is obtained by integrating the assimilation rates over the leaf layers and over the day.

    *Simulation parameters*

    =======  ============================================= =======  ============
     Name     Description                                   Type     Unit
    =======  ============================================= =======  ============
    AMAXTB   Max. leaf CO2 assim. rate as a function of     TCr     kg ha-1 hr-1
             of DVS
    EFFTB    Light use effic. single leaf as a function     TCr     kg ha-1 hr-1 /(J m-2 s-1)
             of daily mean temperature
    KDIFTB   Extinction coefficient for diffuse visible     TCr      -
             as function of DVS
    TMPFTB   Reduction factor of AMAX as function of        TCr      -
             daily mean temperature.
    TMNFTB   Reduction factor of AMAX as function of        TCr      -
             daily minimum temperature.
    =======  ============================================= =======  ============

    *State and rate variables*

    `WOFOST_Assimilation` has no state/rate variables, but calculates the
    rate of assimilation which is returned directly from the `__call__()`
    method.

    *Signals sent or handled*

    None


    *External dependencies:*

    =======  =================================== =================  ============
     Name     Description                         Provided by         Unit
    =======  =================================== =================  ============
    DVS      Crop development stage              DVS_Phenology       -
    LAI      Leaf area index                     Leaf_dynamics       -
    =======  =================================== =================  ============
    """

    def getparameterslist(self):
        return {
            "AMAXTB": {"Description": "Max. leaf CO2 assim. rate as a function of DVS", "Type": "Array",
                       "Mandatory": "True", "UnitOfMeasure": "kg ha-1 hr-1"},
            "EFFTB": {"Description": "Light use effic. single leaf as a function of daily mean temperature",
                      "Type": "Array", "Mandatory": "True", "UnitOfMeasure": "kg ha-1 hr-1 /(J m-2 s-1)"},
            "KDIFTB": {"Description": "Extinction coefficient for diffuse visible as function of DVS", "Type": "Array",
                       "Mandatory": "True", "UnitOfMeasure": "unitless"},
            "TMPFTB": {"Description": "Reduction factor of AMAX as function of daily mean temperature", "Type": "Array",
                       "Mandatory": "True", "UnitOfMeasure": "unitless"},
            "TMNFTB": {"Description": "Reduction factor of AMAX as function of daily minimum temperature",
                       "Type": "Array", "Mandatory": "True", "UnitOfMeasure": "unitless"}
        }

    def setparameters(self, status):
        status.assimilation = Printable()
        status.assimilation.params = Printable()
        cropparams = status.allparameters
        status.assimilation.params.AMAXTB = ecrops.wofost_util.Afgen.Afgen(cropparams['AMAXTB'])
        status.assimilation.params.EFFTB = ecrops.wofost_util.Afgen.Afgen(cropparams['EFFTB'])
        status.assimilation.params.KDIFTB = ecrops.wofost_util.Afgen.Afgen(cropparams['KDIFTB'])
        status.assimilation.params.TMPFTB = ecrops.wofost_util.Afgen.Afgen(cropparams['TMPFTB'])
        status.assimilation.params.TMNFTB = ecrops.wofost_util.Afgen.Afgen(cropparams['TMNFTB'])
        status.assimilation.params.Co2EffectOnAMAX = 1
        status.assimilation.params.Co2EffectOnEFF = 1
        status.assimilation.params.NSTRESS_REDUCTION_FACTOR = 1  # nitrogen stress reduction factor
        return status

    def initialize(self, status):

        status.states.LAI = 0
        status.states.PGASS = 0
        return status

    def runstep(self, status):
        states = status.states
        if (states.DOE is None or status.day < states.DOE) or \
                (states.DOE is not None and status.day >= states.DOE and
                 (
                         states.DOM is not None and status.day >= states.DOM)):  # execute only after emergence and before maturity
            return status

        # CALCULATE INITIAL STATE VARIABLES at sowing/emergence day
        if status.day == status.states.DOS or status.day == status.states.DOE:
            params = status.leafdinamics.params
            FL = status.states.FL
            FR = status.states.FR
            FS = status.states.FS
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
            # Set initial stem biomass
            status.states.WST = (params.TDWI * (1 - FR)) * FS
            status.states.DWST = 0.
            status.states.TWST = status.states.WST + status.states.DWST
            # initial root biomass states
            FR = status.states.FR
            status.states.WRT = params.TDWI * FR
            status.states.DWRT = 0.
            status.states.TWRT = status.states.WRT + status.states.DWRT
            # Initial storage organ biomass
            FO = status.states.FO
            FR = status.states.FR
            status.states.WSO = (params.TDWI * (1 - FR)) * FO
            status.states.DWSO = 0.
            status.states.TWSO = status.states.WSO + status.states.DWSO

        # 2.20  daily dry matter production

        # gross assimilation and correction for sub-optimum
        # average day temperature

        # davide:fix for crops having AMAXTB(2)=0, to make it similar to bioma. Added this IF to manage the case where AMAXTB at the end of the season (DVS=2) is zero: since in bioma it uses DVS+DVR, we do the same at the end of the season
        if status.states.DVS + status.rates.DVR >= status.phenology.params.DVSEND and status.assimilation.params.AMAXTB(
                status.states.DVS + status.rates.DVR) == 0:
            status.states.AMAX = status.assimilation.params.AMAXTB(status.states.DVS + status.rates.DVR)
        else:
            status.states.AMAX = status.assimilation.params.AMAXTB(status.states.DVS)
        status.states.AMAX *= status.assimilation.params.TMPFTB(status.states.DTEMP)

        # davidefuma co2 effect
        status.states.AMAX *= status.assimilation.params.Co2EffectOnAMAX

        # davidefuma N stress effect
        status.states.AMAX *= status.assimilation.params.NSTRESS_REDUCTION_FACTOR

        status.states.KDIF = status.assimilation.params.KDIFTB(status.states.DVS)
        status.states.EFF = status.assimilation.params.EFFTB(status.states.DTEMP)

        # davidefuma co2 effect
        status.states.EFF *= status.assimilation.params.Co2EffectOnEFF

        status.states.DTGA = totass(status.astrodata.DAYL, status.states.AMAX, status.states.EFF, status.states.LAI,
                                    status.states.KDIF, status.states.IRRAD, status.astrodata.DIFPP,
                                    status.astrodata.DSINBE, status.astrodata.SINLD, status.astrodata.COSLD)

        # correction for low minimum temperature potential
        # assimilation in kg CH2O per ha
        status.states.DTGA *= status.assimilation.params.TMNFTB(status.states.TMINRA)
        status.states.PGASS = status.states.DTGA * 30. / 44.

        return status

    def integrate(self, status):
        return status

    def getinputslist(self):
        return {
            "day": {"Description": "Current day", "Type": "Number", "UnitOfMeasure": "doy",
                    "StatusVariable": "status.day"},
            "DOE": {"Description": "Doy of emergence", "Type": "Number", "UnitOfMeasure": "doy",
                    "StatusVariable": "status.states.DOE"},
            "DOM": {"Description": "Doy of maturity", "Type": "Number", "UnitOfMeasure": "doy",
                    "StatusVariable": "status.states.DOM"},

            "DVS": {"Description": "Development stage", "Type": "Number", "UnitOfMeasure": "unitless",
                    "StatusVariable": "status.states.DVS"},
            "DVR": {"Description": "Daily increase in development stage", "Type": "Number", "UnitOfMeasure": "unitless",
                    "StatusVariable": "status.rates.DVR"},
            "DTEMP": {"Description": "Max temperature plus average daily temperature, divided by 2", "Type": "Number",
                      "UnitOfMeasure": "C",
                      "StatusVariable": "status.states.DTEMP"},
            "IRRAD": {"Description": "Daily shortwave radiation",
                      "Type": "Number", "UnitOfMeasure": "J/(m2 day) ",
                      "StatusVariable": "status.states.IRRAD"},
            "LAI": {"Description": "Leaf area index",
                    "Type": "Number", "UnitOfMeasure": "unitless",
                    "StatusVariable": "status.states.LAI"},
            "DAYL": {"Description": " Astronomical daylength (base = 0 degrees)",
                     "Type": "Number", "UnitOfMeasure": "h",
                     "StatusVariable": "status.astrodata.DAYL"},
            "DIFPP": {"Description": "Diffuse irradiation perpendicular to direction of light",
                      "Type": "Number", "UnitOfMeasure": "J m-2 s-1",
                      "StatusVariable": "status.astrodata.DIFPP"},
            "DSINBE": {"Description": " Daily total of effective solar height ",
                       "Type": "Number", "UnitOfMeasure": "s",
                       "StatusVariable": "status.astrodata.DSINBE"},
            "SINLD": {"Description": "Seasonal offset of sine of solar height ",
                      "Type": "Number", "UnitOfMeasure": "unitless",
                      "StatusVariable": "status.astrodata.SINLD"},
            "COSLD": {"Description": "Amplitude of sine of solar height   ",
                      "Type": "Number", "UnitOfMeasure": "unitless",
                      "StatusVariable": "status.astrodata.COSLD"},

        }

    def getoutputslist(self):
        return {
            "PGASS": {"Description": "", "Type": "Number", "UnitOfMeasure": "",
                      "StatusVariable": "status.states.PGASS"},
            "DTGA": {"Description": "", "Type": "Number", "UnitOfMeasure": "",
                     "StatusVariable": "status.states.DTGA"},
            "EFF": {"Description": "", "Type": "Number", "UnitOfMeasure": "",
                    "StatusVariable": "status.states.EFF"},
            "KDIF": {"Description": "", "Type": "Number", "UnitOfMeasure": "",
                     "StatusVariable": "status.states.KDIF"},
            "AMAX": {"Description": "", "Type": "Number", "UnitOfMeasure": "",
                     "StatusVariable": "status.states.AMAX"},

        }
