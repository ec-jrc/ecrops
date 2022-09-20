import array
from math import exp

from ecrops.wofost_util.util import limit

import ecrops.wofost_util.Afgen
from ..Printable import Printable


class Evapotranspiration():
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
    EVWMX    Maximum evaporation rate from an open water        Y    |cm day-1|
             surface.
    EVSMX    Maximum evaporation rate from a wet soil surface.  Y    |cm day-1|
    TRAMX    Maximum transpiration rate from the plant canopy   Y    |cm day-1|
    TRA      Actual transpiration rate from the plant canopy    Y    |cm day-1|
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
                      "UnitOfMeasure": "unitless"}
        }

    def setparameters(self, status):
        status.evapotranspiration = Printable()
        status.evapotranspiration.params = Printable()
        cropparams = status.allparameters
        status.evapotranspiration.params.USE_HERMES_FRROOT = False
        if hasattr(status, 'USE_HERMES_FRROOT'):
            status.evapotranspiration.params.USE_HERMES_FRROOT = status.USE_HERMES_FRROOT
        status.evapotranspiration.params.CFET = cropparams['CFET']
        status.evapotranspiration.params.DEPNR = cropparams['DEPNR']
        status.evapotranspiration.params.KDIFTB = ecrops.wofost_util.Afgen.Afgen(cropparams['KDIFTB'])
        status.evapotranspiration.params.IAIRDU = cropparams['IAIRDU']
        status.evapotranspiration.params.IOX = cropparams['IOX']
        if 'CRAIRC' in status.soildata:
            status.evapotranspiration.params.CRAIRC = status.soildata['CRAIRC']
        else:
            status.evapotranspiration.params.CRAIRC = 0

        if 'SM0' in status.soildata:
            status.evapotranspiration.params.SM0 = status.soildata['SM0']
        if 'SMW' in status.soildata:
            status.evapotranspiration.params.SMW = status.soildata['SMW']

        if (not 'NSL' in status.soildata) or status.soildata['NSL'] == 0:
            if 'SMFCF' in status.soildata:
                status.evapotranspiration.params.SMFCF = status.soildata['SMFCF']
                status.states.SM = status.soildata['SMFCF']
        else:
            for il in range(0, status.soildata['NSL']):
                status.soildata['SOIL_LAYERS'][il].SM = status.soildata['SOIL_LAYERS'][il].SMFCF

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
        status.states._DSOS = 0
        status.states._IDWST = 0
        status.states._IDOST = 0
        status.rates.TRALY = 0

        # Reduction factor for transpiration in case of water shortage (RFWS)
        status.rates.RFWS = 1

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

    def runstep(self, status):
        p = status.evapotranspiration.params
        r = status.rates
        s = status.states

        # start calculating the water balance only after emergence
        if s.DOE is None or (status.day - s.DOE).days < 0:
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

        # davidefuma co2 effect
        # print('status.evapotranspiration.params.Co2EffectOnPotentialTraspiration=' + str(status.evapotranspiration.params.Co2EffectOnPotentialTraspiration))
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

                # count days since start oxygen shortage (up to 4 days)
                if SM >= SMAIR:
                    status.states._DSOS = min((status.states._DSOS + 1), 4)
                else:
                    status.states._DSOS = 0

                # maximum reduction reached after 4 days
                RFOSMX = limit(0., 1., (p.SM0 - SM) / (p.SM0 - SMAIR))
                RFOS = RFOSMX + (1. - status.states._DSOS / 4.) * (1. - RFOSMX)

            # For rice, or non-rice crops grown on well drained land
            elif p.IAIRDU == 1 or p.IOX == 0:
                RFOS = 1.
            # Transpiration rate multiplied with reduction factors for oxygen and
            # water
            r.TRA = r.TRAMX * RFOS * status.rates.RFWS


        else:  # in case of layered soil, calculate the transpiration for each layer
            if 'SOIL_LAYERS' in status.soildata:
                # calculation critical soil moisture content
                DEPTH = 0.0
                SUMTRA = 0.0

                TRALY = array.array('d', [0.0] * s.NSL)
                for il in range(0, s.NSL):
                    SM0 = s.SOIL_LAYERS[il].SM0
                    SMW = s.SOIL_LAYERS[il].SMW
                    SMFCF = s.SOIL_LAYERS[il].SMFCF
                    CRAIRC = s.SOIL_LAYERS[il].CRAIRC

                    SMCR = (1. - SWDEP) * (SMFCF - SMW) + SMW
                    # reduction in transpiration in case of water shortage
                    status.rates.RFWS = limit(0., 1., (s.SOIL_LAYERS[il].SM - SMW) / (SMCR - SMW))

                    # reduction in transpiration in case of oxygen shortage
                    # for non-rice crops, and possibly deficient land drainage
                    if (p.IAIRDU == 0 and p.IOX == 1):
                        # critical soil moisture content for aeration
                        SMAIR = SM0 - CRAIRC
                        # count days since start oxygen shortage (up to 4 days)
                        if (s.SOIL_LAYERS[il].SM >= SMAIR): self._DSOS = min((self._DSOS + 1.), 4.)
                        if (s.SOIL_LAYERS[il].SM < SMAIR): self._DSOS = 0.
                        # maximum reduction reached after 4 days
                        RFOSMX = limit(0., 1., (SM0 - s.SOIL_LAYERS[il].SM) / (SM0 - SMAIR))
                        RFOS = RFOSMX + (1. - self._DSOS / 4.) * (1. - RFOSMX)

                    # for rice, or non-rice crops grown on perfectly drained land
                    elif (p.IAIRDU == 1 or p.IOX == 0):
                        RFOS = 1.

                    if status.evapotranspiration.params.USE_HERMES_FRROOT:
                        # davidefuma 28-02-2022 multiply FRROOT per the factor of distribution of roots calculated by hermes root depth
                        FRROOT = status.hermesrootdepth.hermes_roots_layer_data[il].percentageOfRootInLayer / 100
                    else:  # original FRROOT based on ration between layer depth and root depth
                        FRROOT = max(0.0, (min(s.RD, DEPTH + s.SOIL_LAYERS[il].TSL) - DEPTH)) / s.RD

                    TRALY[il] = status.rates.RFWS * RFOS * r.TRAMX * FRROOT
                    DEPTH += s.SOIL_LAYERS[il].TSL
                r.TRA = sum(TRALY)
                r.TRALY = TRALY
                # r.TRA=r.TRAMX #TODO:eliminazione water stress!! Nel funzionamento normale, commentare questa riga!
                r.WaterStressReductionFactor = r.TRA / r.TRAMX
            else:
                RFOS = 1.
        # Counting stress days
        if status.rates.RFWS < 1.:
            r.IDWS = True
            status.states._IDWST += 1
        if RFOS < 1.:
            r.IDOS = True
            status.states._IDOST += 1

        return status
