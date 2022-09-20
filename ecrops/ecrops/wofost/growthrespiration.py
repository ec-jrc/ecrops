from ..Printable import Printable


class WOFOST_GrowthRespiration:
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
