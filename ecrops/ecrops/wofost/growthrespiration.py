# -*- coding: utf-8 -*-
# This component is derived from PCSE software/Wofost model
# (Copyright @ 2004-2014 Alterra, Wageningen-UR; Allard de Wit allard.dewit@wur.nl, April 2014)
# and modified by EC-JRC for the eCrops framework under the European Union Public License (EUPL), Version 1.2
# European Commission, Joint Research Centre, March 2023



from ..Printable import Printable
from ecrops.Step import Step

class WOFOST_GrowthRespiration(Step):
    """This step implements a growth respiration model for the WOFOST crop model."""

    def getparameterslist(self):
        return {
            "CVL": {"Description": "Conversion factor for assimilates to leaves", "Type": "Number", "Mandatory": "True",
                    "UnitOfMeasure": "unitless"},
            "CVR": {"Description": "Conversion factor for assimilates to roots", "Type": "Number", "Mandatory": "True",
                    "UnitOfMeasure": "unitless"},
            "CVO": {"Description": "Conversion factor for assimilates to storage organs", "Type": "Number",
                    "Mandatory": "True",
                    "UnitOfMeasure": "unitless"},
            "CVS": {"Description": "Conversion factor for assimilates to stems", "Type": "Number", "Mandatory": "True",
                    "UnitOfMeasure": "unitless"}
        }

    def setparameters(self, status):
        status.growthrespiration = Printable()
        status.growthrespiration.params = Printable()
        cropparams = status.allparameters
        status.growthrespiration.params.CVS = cropparams['CVS']
        status.growthrespiration.params.CVR = cropparams['CVR']
        status.growthrespiration.params.CVL = cropparams['CVL']
        status.growthrespiration.params.CVO = cropparams['CVO']

        return status

    def initialize(self, status):
        rates = status.rates
        rates.DMI = 0
        rates.ADMI = 0

        return status

    def runstep(self, status):
        states = status.states
        if (states.DOE is None or status.day < states.DOE) or (states.DOE is not None and status.day >= states.DOE and (
                states.DOM is not None and status.day >= states.DOM)):  # execute only after emergence and before maturity
            return status

        rates = status.rates
        states = status.states
        params = status.growthrespiration.params

        # Respiration
        rates.MRES = min(rates.GASS, rates.PMRES)

        # Net available assimilates
        rates.ASRC = rates.GASS - rates.MRES

        CVF = 1. / ((states.FL / params.CVL + states.FS / params.CVS + states.FO / params.CVO) *
                    (1. - states.FR) + states.FR / params.CVR)
        rates.DMI = CVF * rates.ASRC
        rates.ADMI = (1. - states.FR) * rates.DMI
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
            "FR": {"Description": "Partitioning to roots", "Type": "Number", "UnitOfMeasure": "unitless",
                   "StatusVariable": "status.states.FR"},
            "FL": {"Description": "Partitioning to leaves", "Type": "Number", "UnitOfMeasure": "unitless",
                   "StatusVariable": "status.states.FL"},
            "FS": {"Description": "Partitioning to stems", "Type": "Number", "UnitOfMeasure": "unitless",
                   "StatusVariable": "status.states.FS"},
            "FO": {"Description": "Partitioning to storage organs", "Type": "Number", "UnitOfMeasure": "unitless",
                   "StatusVariable": "status.states.FO"},
            "GASS": {"Description": "", "Type": "Number", "UnitOfMeasure": "",
                   "StatusVariable": "status.rates.GASS"},
            "PMRES": {"Description": "", "Type": "Number", "UnitOfMeasure": "",
                   "StatusVariable": "status.rates.PMRES"},

        }
    def getoutputslist(self):
        return {
            "DMI": {"Description": "Daily increase in root depth", "Type": "Number", "UnitOfMeasure": "cm",
                   "StatusVariable": "status.rates.DMI"},
            "ADMI": {"Description": "Daily increase in above-ground dry matter", "Type": "Number", "UnitOfMeasure": "Kg/ha",
                    "StatusVariable": "status.rates.ADMI"},
            "ASRC": {"Description": "Available respiration", "Type": "Number", "UnitOfMeasure": " kg CH2O kg-1",
                     "StatusVariable": "status.rates.ASRC"},
            "MRES": {"Description": "Relative maintenance respiration", "Type": "Number", "UnitOfMeasure": " kg CH2O kg-1",
                     "StatusVariable": "status.rates.MRES"},
        }