# -*- coding: utf-8 -*-
# This component is derived from PCSE software/Wofost model
# (Copyright @ 2004-2014 Alterra, Wageningen-UR; Allard de Wit allard.dewit@wur.nl, April 2014)
# and modified by EC-JRC for the eCrops framework under the European Union Public License (EUPL), Version 1.2
# European Commission, Joint Research Centre, March 2023



from math import exp

import ecrops.wofost_util.Afgen
from ..Printable import Printable


class EvapotranspirationPotential():
    """Calculation of evaporation (water and soil) and transpiration rates.

    Simulation parameters:

    =======  ============================================= =======  ============
     Name     Description                                   Type     Unit
    =======  ============================================= =======  ============
    CFET     Correction factor for potential transpiration   SCr       -
             rate.

    KDIFTB   Extinction coefficient for diffuse visible      TCr       -
             as function of DVS.
    =======  ============================================= =======  ============




    Rate variables

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    EVWMX    Maximum evaporation rate from an open water        Y    |cm day-1|
             surface.
    EVSMX    Maximum evaporation rate from a wet soil surface.  Y    |cm day-1|
    TRAMX    Maximum transpiration rate from the plant canopy   Y    |cm day-1|
    TRA      Actual transpiration rate from the plant canopy    Y    |cm day-1|

    =======  ================================================= ==== ============

    Signals send or handled

    None

    External dependencies:

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
            "KDIFTB": {"Description": "Extinction coefficient for diffuse visible as function of DVS", "Type": "Number",
                       "Mandatory": "True",
                       "UnitOfMeasure": "unitless"},

        }

    def setparameters(self, status):
        status.evapotranspiration = Printable()
        status.evapotranspiration.params = Printable()
        cropparams = status.allparameters

        status.evapotranspiration.params.CFET = cropparams['CFET']
        status.evapotranspiration.params.KDIFTB = ecrops.wofost_util.Afgen.Afgen(cropparams['KDIFTB'])



        return status

    def integrate(self, status):
        return status

    def initialize(self, status):

        status.rates.TRA = 100
        status.rates.TRAMX = 100
        status.rates.EVWMX = 0
        status.rates.EVSMX = 0


        return status


    def runstep(self, status):
        p = status.evapotranspiration.params
        r = status.rates
        s = status.states

        if s.DOE is None or status.day < s.DOE:  # execute only after emergence
            return status

        DVS = status.states.DVS
        LAI = status.states.LAI



        KGLOB = 0.75 * p.KDIFTB(DVS)

        # crop specific correction on potential transpiration rate
        ET0 = p.CFET * status.states.ET0

        # maximum evaporation and transpiration rates
        EKL = round(exp(-KGLOB * LAI), 12)

        # davidefuma co2 effect
        # print('status.evapotranspiration.params.Co2EffectOnPotentialTraspiration=' + str(status.evapotranspiration.params.Co2EffectOnPotentialTraspiration))
        EKL *= float(status.evapotranspiration.params.Co2EffectOnPotentialTraspiration)

        r.EVWMX = status.states.E0 * EKL
        r.EVSMX = max(0., status.states.ES0 * EKL)
        r.TRAMX = max(0.000001, ET0 * (1. - EKL))
        r.TRA = r.TRAMX


        return status


