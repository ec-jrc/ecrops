# -*- coding: utf-8 -*-
# This component is derived from PCSE software/Wofost model
# (Copyright @ 2004-2014 Alterra, Wageningen-UR; Allard de Wit allard.dewit@wur.nl, April 2014)
# and modified by EC-JRC for the eCrops framework under the European Union Public License (EUPL), Version 1.2
# European Commission, Joint Research Centre, March 2023


from ..Printable import Printable
from ecrops.Step import Step

class WOFOST_Storage_Organ_Dynamics(Step):
    """Implementation of storage organ dynamics.

    Storage organs are the most simple component of the plant in WOFOST and
    consist of a static pool of biomass. Growth of the storage organs is the
    result of assimilate partitioning. Death of storage organs is not
    implemented and the corresponding rate variable (DRSO) is always set to
    zero.

    Pods are green elements of the plant canopy and can as such contribute
    to the total photosynthetic active area. This is expressed as the Pod
    Area Index which is obtained by multiplying pod biomass with a fixed
    Specific Pod Area (SPA).

    **Simulation parameters**

    =======  ============================================= =======  ============
     Name     Description                                   Type     Unit
    =======  ============================================= =======  ============
    TDWI     Initial total crop dry weight                  SCr      kg ha-1
    SPA      Specific Pod Area                              SCr      ha kg-1
    =======  ============================================= =======  ============

    **State variables**

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    PAI      Pod Area Index                                     Y     -
    WSO      Weight of living storage organs                    Y     kg ha-1
    DWSO     Weight of dead storage organs                      N     kg ha-1
    TWSO     Total weight of storage organs                     Y     kg ha-1
    =======  ================================================= ==== ============

    **Rate variables**

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    GRSO     Growth rate storage organs                         N   kg ha-1 d-1
    DRSO     Death rate storage organs                          N   kg ha-1 d-1
    GWSO     Net change in storage organ biomass                N   kg ha-1 d-1
    =======  ================================================= ==== ============

    **Signals send or handled**

    None

    **External dependencies**

    =======  =================================== =================  ============
     Name     Description                         Provided by         Unit
    =======  =================================== =================  ============
    ADMI     Above-ground dry matter             CropSimulation     kg ha-1 d-1
             increase
    FO       Fraction biomass to storage organs  DVS_Partitioning    -
    FR       Fraction biomass to roots           DVS_Partitioning    -
    =======  =================================== =================  ============
    """

    def getparameterslist(self):
        return {
            "SPA": {"Description": "Specific Pod Area", "Type": "Number", "Mandatory": "True",
                    "UnitOfMeasure": "ha kg-1"},
            "TDWI": {"Description": "Initial total crop dry weight", "Type": "Number", "Mandatory": "True",
                     "UnitOfMeasure": "kg ha-1"}
        }

    def setparameters(self, status):
        status.storageorgansdynamics = Printable()
        status.storageorgansdynamics.params = Printable()
        cropparams = status.allparameters
        status.storageorgansdynamics.params.SPA = cropparams['SPA']
        status.storageorgansdynamics.params.TDWI = cropparams['TDWI']
        return status

    def initialize(self, status):
        status.states.WSO = 0.
        status.states.DWSO = 0.
        status.states.TWSO = 0.
        status.states.PAI = 0.

        status.rates.GRSO = 0.
        status.rates.DRSO = 0.0
        status.rates.GWSO = 0.
        status.states.PAI = 0.
        return status

    def runstep(self, status):
        states = status.states
        status.rates.GRSO = 0.
        status.rates.DRSO = 0.0
        status.rates.GWSO = 0.

        # INITIAL STATES at sowing/emergence day
        if status.day == status.states.DOS or status.day == status.states.DOE:
            params = status.storageorgansdynamics.params
            # Initial storage organ biomass
            FO = status.states.FO
            FR = status.states.FR
            status.states.WSO = (params.TDWI * (1 - FR)) * FO
            status.states.DWSO = 0.
            status.states.TWSO = status.states.WSO + status.states.DWSO
            # Initial Pod Area Index
            status.states.PAI = status.states.WSO * params.SPA

        if (states.DOE is None or status.day < states.DOE) or (states.DOE is not None and status.day >= states.DOE and (
                states.DOM is not None and status.day >= states.DOM)):  # execute only after emergence and before maturity
            return status

        rates = status.rates

        params = status.storageorgansdynamics.params

        FO = status.states.FO
        ADMI = status.rates.ADMI

        # Growth/death rate organs
        rates.GRSO = ADMI * FO
        rates.DRSO = 0.0
        rates.GWSO = rates.GRSO - rates.DRSO

        return status

    def integrate(self, status):
        rates = status.rates
        states = status.states
        params = status.storageorgansdynamics.params

        # Stem biomass (living, dead, total)
        states.WSO += rates.GWSO
        states.DWSO += rates.DRSO
        states.TWSO = states.WSO + states.DWSO

        # Calculate Pod Area Index (SAI)
        states.PAI = states.WSO * params.SPA


        return status

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
            "FO": {"Description": "Partitioning to storage organs", "Type": "Number", "UnitOfMeasure": "unitless",
                   "StatusVariable": "status.states.FO"},
            "FR": {"Description": "Partitioning to roots", "Type": "Number", "UnitOfMeasure": "unitless",
                   "StatusVariable": "status.states.FR"},
            "ADMI": {"Description": "Daily increase in above-ground dry matter", "Type": "Number",
                     "UnitOfMeasure": "Kg/ha",
                     "StatusVariable": "status.rates.ADMI"},
            "WSO": {"Description": " Dry weight of living storage organs", "Type": "Number", "UnitOfMeasure": "Kg/ha",
                    "StatusVariable": "status.states.WSO"},
            "DWSO": {"Description": "Dry weight of dead storage organs", "Type": "Number", "UnitOfMeasure": "Kg/ha",
                     "StatusVariable": "status.states.DWSO"},
            "TWSO": {"Description": "Total weight dry + living storage organs", "Type": "Number",
                     "UnitOfMeasure": "Kg/ha",
                     "StatusVariable": "status.states.TWSO"},

        }

    def getoutputslist(self):
        return {
            "PAI": {"Description": "Pod area index",
                    "Type": "Number", "UnitOfMeasure": "unitless",
                    "StatusVariable": "status.states.PAI"},
            "GRSO": {"Description": "Daily increase of dry weight of living storage organs", "Type": "Number",
                     "UnitOfMeasure": "Kg/ha",
                     "StatusVariable": "status.rates.GRSO"},
            "DRSO": {"Description": "Daily increase of dry weight of dead storage organs", "Type": "Number",
                     "UnitOfMeasure": "Kg/ha",
                     "StatusVariable": "status.rates.DRSO"},
            "GWSO": {"Description": "Daily increase of total weight dry + living storage organs", "Type": "Number",
                     "UnitOfMeasure": "Kg/ha",
                     "StatusVariable": "status.rates.GWSO"},
            "WSO": {"Description": " Dry weight of living storage organs", "Type": "Number", "UnitOfMeasure": "Kg/ha",
                    "StatusVariable": "status.states.WSO"},
            "DWSO": {"Description": "Dry weight of dead storage organs", "Type": "Number", "UnitOfMeasure": "Kg/ha",
                     "StatusVariable": "status.states.DWSO"},
            "TWSO": {"Description": "Total weight dry + living storage organs", "Type": "Number", "UnitOfMeasure": "Kg/ha",
                     "StatusVariable": "status.states.TWSO"},

        }
