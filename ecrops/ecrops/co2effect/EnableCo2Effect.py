from ecrops.Step import Step

class EnableCo2Effect(Step):
    """When this step is inserted in a workflow after the 'DisableCo2Effect' step, it re-enables the CO2 effects on plant."""

    def getparameterslist(self):
        return {}  # no parameters in this step

    def setparameters(self, status):
        return status

    def initialize(self, status):
        return status

    def runstep(self, status):
        status.co2data.Co2EffectOnAMAX = status.co2data.TempCo2EffectOnAMAX
        status.co2data.Co2EffectOnEFF = status.co2data.TempCo2EffectOnEFF
        status.co2data.Co2EffectOnPotentialTraspiration = status.co2data.TempCo2EffectOnPotentialTraspiration
        status.co2data.DMI_NoCo2 = status.rates.DMI
        return status

    def integrate(self, status):
        return status

    def getinputslist(self):
        return {

            "TempCo2EffectOnAMAX": {"Description": "Co2 Effect On AMAX",
                     "Type": "Number", "UnitOfMeasure": "unitless",
                     "StatusVariable": "status.co2data.TempCo2EffectOnAMAX"},
            "TempCo2EffectOnEFF": {"Description": "Co2 Effect On EFF",
                                "Type": "Number", "UnitOfMeasure": "unitless",
                                "StatusVariable": "status.co2data.TempCo2EffectOnEFF"},
            "TempCo2EffectOnPotentialTraspiration": {"Description": "Co2 Effect On potential transpiration",
                                   "Type": "Number", "UnitOfMeasure": "unitless",
                                   "StatusVariable": "status.co2data.TempCo2EffectOnPotentialTraspiration"},
            "DMI": {"Description": "Daily increase of total dry matter", "Type": "Number", "UnitOfMeasure": "unitless",
                    "StatusVariable": "status.rates.DMI"},
        }


    def getoutputslist(self):
        return {

            "Co2EffectOnAMAX": {"Description": "Co2 Effect On AMAX",
                                    "Type": "Number", "UnitOfMeasure": "unitless",
                                    "StatusVariable": "status.co2data.Co2EffectOnAMAX"},
            "Co2EffectOnEFF": {"Description": "Co2 Effect On EFF",
                                   "Type": "Number", "UnitOfMeasure": "unitless",
                                   "StatusVariable": "status.co2data.Co2EffectOnEFF"},
            "Co2EffectOnPotentialTraspiration": {"Description": "Co2 Effect On potential transpiration",
                                                     "Type": "Number", "UnitOfMeasure": "unitless",
                                                     "StatusVariable": "status.co2data.Co2EffectOnPotentialTraspiration"},
            "DMI_NoCo2": {"Description": "Daily increase of total dry matter", "Type": "Number", "UnitOfMeasure": "unitless",
                    "StatusVariable": "status.co2data.DMI_NoCo2"},

        }
