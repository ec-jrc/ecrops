# -*- coding: utf-8 -*-
# This component is derived from PCSE software/Wofost model
# (Copyright @ 2004-2014 Alterra, Wageningen-UR; Allard de Wit allard.dewit@wur.nl, April 2014)
# and modified by EC-JRC for the eCrops framework under the European Union Public License (EUPL), Version 1.2
# European Commission, Joint Research Centre, March 2023


import ecrops.wofost_util.Afgen
from ..Printable import Printable


class WOFOST_Root_Dynamics:
    """Root biomass dynamics and rooting depth.

    Root growth and root biomass dynamics in WOFOST are separate processes,
    with the only exception that root growth stops when no more biomass is sent
    to the root system.

    Root biomass increase results from the assimilates partitioned to
    the root system. Root death is defined as the current root biomass
    multiplied by a relative death rate (`RDRRTB`). The latter as a function
    of the development stage (`DVS`).

    Increase in root depth is a simple linear expansion over time unti the
    maximum rooting depth (`RDM`) is reached.

    **Simulation parameters**

    =======  ============================================= =======  ============
     Name     Description                                   Type     Unit
    =======  ============================================= =======  ============
    RDI      Initial rooting depth                          SCr      cm
    RRI      Daily increase in rooting depth                SCr      |cm day-1|
    RDMCR    Maximum rooting depth of the crop              SCR      cm
    RDMSOL   Maximum rooting depth of the soil              SSo      cm
    TDWI     Initial total crop dry weight                  SCr      |kg ha-1|
    IAIRDU   Presence of air ducts in the root (1) or       SCr      -
             not (0)
    RDRRTB   Relative death rate of roots as a function     TCr      -
             of development stage
    =======  ============================================= =======  ============


    **State variables**

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    RD       Current rooting depth                              Y     cm
    RDM      Maximum attainable rooting depth at the minimum    N     cm
             of the soil and crop maximum rooting depth
    WRT      Weight of living roots                             Y     |kg ha-1|
    DWRT     Weight of dead roots                               N     |kg ha-1|
    TWRT     Total weight of roots                              Y     |kg ha-1|
    =======  ================================================= ==== ============

    **Rate variables**

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    RR       Growth rate root depth                             N    cm
    GRRT     Growth rate root biomass                           N   |kg ha-1 d-1|
    DRRT     Death rate root biomass                            N   |kg ha-1 d-1|
    GWRT     Net change in root biomass                         N   |kg ha-1 d-1|
    =======  ================================================= ==== ============

    **Signals send or handled**

    None

    **External dependencies:**

    =======  =================================== =================  ============
     Name     Description                         Provided by         Unit
    =======  =================================== =================  ============
    DVS      Crop development stage              DVS_Phenology       -
    DMI      Total dry matter                    CropSimulation     |kg ha-1 d-1|
             increase
    FR       Fraction biomass to roots           DVS_Partitioning    -
    =======  =================================== =================  ============
    """

    def getparameterslist(self):
        return {
            "RDI": {"Description": "Initial root depth", "Type": "Number", "Mandatory": "True", "UnitOfMeasure": "cm"},
            "RRI": {"Description": "Daily increase in rooting depth", "Type": "Number", "Mandatory": "True",
                    "UnitOfMeasure": "cm day-1"},
            "RDMCR": {"Description": "Maximum rooting depth of the crop", "Type": "Number", "Mandatory": "True",
                      "UnitOfMeasure": "cm"},
            "RDMSOL": {"Description": "Maximum rooting depth of the soil", "Type": "Number", "Mandatory": "True",
                       "UnitOfMeasure": "cm"},
            "TDWI": {"Description": "Initial total crop dry weight ", "Type": "Number", "Mandatory": "True",
                     "UnitOfMeasure": "Kg ha-1"},
            "IAIRDU": {"Description": "Presence of air ducts in the root (1) or not (0)", "Type": "Number",
                       "Mandatory": "True", "UnitOfMeasure": "unitless"},
            "RDRRTB": {"Description": "Relative death rate of roots as a function of development stage",
                       "Type": "Array", "Mandatory": "True", "UnitOfMeasure": "unitless"}
        }

    def setparameters(self, status):
        status.rootdinamics = Printable()
        status.rootdinamics.params = Printable()
        cropparams = status.allparameters
        status.rootdinamics.params.RDI = cropparams['RDI']
        status.rootdinamics.params.RRI = cropparams['RRI']
        status.rootdinamics.params.RDMCR = cropparams['RDMCR']
        status.rootdinamics.params.RDMSOL = status.soildata['RDMSOL']
        status.rootdinamics.params.TDWI = cropparams['TDWI']
        status.rootdinamics.params.IAIRDU = cropparams['IAIRDU']
        status.rootdinamics.params.RDRRTB = ecrops.wofost_util.Afgen.Afgen(cropparams['RDRRTB'])
        return status

    def initialize(self, status):

        params = status.rootdinamics.params
        rdmax = max(params.RDI, min(params.RDMCR, params.RDMSOL))
        status.states.RDM = rdmax
        status.states.RD = 0
        status.states.WRT = 0
        status.states.DWRT = 0
        status.states.TWRT = 0
        status.rates.GRRT = 0
        status.rates.DRRT = 0
        status.rates.GWRT = 0
        status.rates.RR = 0.
        status.states.WRT_previousDay = 0.

        return status

    def runstep(self, status):

        states = status.states
        status.rates.GRRT = 0
        status.rates.DRRT = 0
        status.rates.GWRT = 0
        status.rates.RR = 0.

        # INITIAL STATES at sowing/emergence day
        if status.day == status.states.DOS or status.day == status.states.DOE:
            params = status.rootdinamics.params
            status.states.RD = params.RDI
            # initial root biomass states
            FR = status.states.FR
            status.states.WRT = params.TDWI * FR
            status.states.DWRT = 0.
            status.states.TWRT = status.states.WRT + status.states.DWRT
            states.WRT_previousDay = 0


        if (states.DOE is None or status.day < states.DOE) or (states.DOE is not None and status.day >= states.DOE and (
                states.DOM is not None and status.day >= states.DOM)):  # execute only after emergence and before maturity
            return status

        params = status.rootdinamics.params
        rates = status.rates
        states = status.states

        # Increase in root biomass
        DMI = status.rates.DMI
        DVS = status.states.DVS
        FR = status.states.FR
        rates.GRRT = FR * DMI
        rates.DRRT = states.WRT * params.RDRRTB(DVS)
        rates.GWRT = rates.GRRT - rates.DRRT

        # Increase in root depth
        rates.RR = min((states.RDM - states.RD), params.RRI)
        # Do not let the roots growth if partioning to the roots
        # (variable FR) is zero.
        if FR == 0.:
            rates.RR = 0.

        return status

    def integrate(self, status):
        rates = status.rates
        states = status.states
        params = status.rootdinamics.params

        states.WRT_previousDay = states.WRT

        # Dry weight of living roots
        states.WRT += rates.GWRT
        # Dry weight of dead roots
        states.DWRT += rates.DRRT
        # Total weight dry + living roots
        states.TWRT = states.WRT + states.DWRT

        # New root depth
        states.RD += rates.RR
        return status
