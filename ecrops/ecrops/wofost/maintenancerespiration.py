# -*- coding: utf-8 -*-
# This component is derived from PCSE software/Wofost model
# (Copyright @ 2004-2014 Alterra, Wageningen-UR; Allard de Wit allard.dewit@wur.nl, April 2014)
# and modified by EC-JRC for the eCrops framework under the European Union Public License (EUPL), Version 1.2
# European Commission, Joint Research Centre, March 2023


import ecrops.wofost_util.Afgen
from ..Printable import Printable


class WOFOST_Maintenance_Respiration:
    """Maintenance respiration in WOFOST

    WOFOST calculates the maintenance respiration as proportional to the dry
    weights of the plant organs to be maintained, where each plant organ can be
    assigned a different maintenance coefficient. Multiplying organ weight
    with the maintenance coeffients yields the relative maintenance respiration
    (`RMRES`) which is than corrected for senescence (parameter `RFSETB`). Finally,
    the actual maintenance respiration rate is calculated using the daily mean
    temperature, assuming a relative increase for each 10 degrees increase
    in temperature as defined by `Q10`.

    **Simulation parameters:** (To be provided in cropdata dictionary):

    =======  ============================================= =======  ============
     Name     Description                                   Type     Unit
    =======  ============================================= =======  ============
    Q10      Relative increase in maintenance repiration    SCr       -
             rate with each 10 degrees increase in
             temperature
    RMR      Relative maintenance respiration rate for
             roots                                          SCr     |kg CH2O kg-1 d-1|
    RMS      Relative maintenance respiration rate for
             stems                                          SCr     |kg CH2O kg-1 d-1|
    RML      Relative maintenance respiration rate for
             leaves                                         SCr     |kg CH2O kg-1 d-1|
    RMO      Relative maintenance respiration rate for
             storage organs                                 SCr     |kg CH2O kg-1 d-1|
    =======  ============================================= =======  ============


    **State and rate variables:**

    `WOFOSTMaintenanceRespiration` has no state/rate variables, but calculates
    the rate of respiration which is returned directly from the `__call__()`
    method.

    **Signals send or handled**

    None

    **External dependencies:**

    =======  =================================== =============================  ============
     Name     Description                         Provided by                    Unit
    =======  =================================== =============================  ============
    DVS      Crop development stage              DVS_Phenology                  -
    WRT      Dry weight of living roots          WOFOST_Root_Dynamics           |kg ha-1|
    WST      Dry weight of living stems          WOFOST_Stem_Dynamics           |kg ha-1|
    WLV      Dry weight of living leaves         WOFOST_Leaf_Dynamics           |kg ha-1|
    WSO      Dry weight of living storage organs WOFOST_Storage_Organ_Dynamics  |kg ha-1|
    =======  =================================== =============================  ============


    """

    def getparameterslist(self):
        return {
            "Q10": {
                "Description": "Relative increase in maintenance repiration rate with each 10 degrees increase in temperature",
                "Type": "Number", "Mandatory": "True", "UnitOfMeasure": "unitless"},
            "RMR": {"Description": "Relative maintenance respiration rate for roots", "Type": "Number",
                    "Mandatory": "True", "UnitOfMeasure": "kg CH2O kg-1 d-1"},
            "RML": {"Description": "Relative maintenance respiration rate for leaves", "Type": "Number",
                    "Mandatory": "True", "UnitOfMeasure": "kg CH2O kg-1 d-1"},
            "RMS": {"Description": "Relative maintenance respiration rate for stems", "Type": "Number",
                    "Mandatory": "True", "UnitOfMeasure": "kg CH2O kg-1 d-1"},
            "RMO": {"Description": "Relative maintenance respiration rate for storage organs", "Type": "Number",
                    "Mandatory": "True", "UnitOfMeasure": "kg CH2O kg-1 d-1"},
            "RFSETB": {"Description": "Reduction factor for senescence as function of DVS", "Type": "Array",
                       "Mandatory": "True", "UnitOfMeasure": "unitless"}
        }

    def setparameters(self, status):
        status.maintenancerespiration = Printable()
        status.maintenancerespiration.params = Printable()
        cropparams = status.allparameters
        status.maintenancerespiration.params.Q10 = cropparams['Q10']
        status.maintenancerespiration.params.RMR = cropparams['RMR']
        status.maintenancerespiration.params.RML = cropparams['RML']
        status.maintenancerespiration.params.RMS = cropparams['RMS']
        status.maintenancerespiration.params.RMO = cropparams['RMO']
        status.maintenancerespiration.params.RFSETB = ecrops.wofost_util.Afgen.Afgen(cropparams['RFSETB'])
        return status

    def initialize(self, status):
        status.states.WRT = 0
        status.states.WLV = 0
        status.states.WST = 0
        status.states.WSO = 0

        return status

    def runstep(self, status):
        states = status.states
        if (states.DOE is None or status.day < states.DOE) or (
                states.DOE is not None and status.day >= states.DOE and (
                states.DOM is not None and status.day >= states.DOM)):  # execute only after emergence and before maturity
            return status

        p = status.maintenancerespiration.params

        # water stress reduction
        TRA = status.rates.TRA
        TRAMX = status.rates.TRAMX
        status.rates.GASS = status.states.PGASS * TRA / TRAMX

        status.rates.RMRES = (p.RMR * status.states.WRT +
                              p.RML * status.states.WLV + \
                              p.RMS * status.states.WST + \
                              p.RMO * status.states.WSO)
        status.rates.RMRES *= p.RFSETB(status.states.DVS)
        status.rates.TEFF = p.Q10 ** ((status.states.TEMP - 25.) / 10.)
        status.rates.PMRES = status.rates.RMRES * status.rates.TEFF
        status.rates.MRES = min(status.rates.GASS, status.rates.PMRES)
        return status

    def integrate(self, status):
        return status
