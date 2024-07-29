from ecrops.Step import Step
class DisableCo2Effect(Step):
    """When this step is inserted in a workflow, it disables the CO2 effect on plant, by setting all the effects coefficients to 1.
    All the calculated effect are saved in temporary variables and can be reactivated by putting in the workflow the 'EnableCO2Effect' step
     """

    def getparameterslist(self):
        return {}#no parameters in this step

    def setparameters(self,status):
        return status



    def initialize(self,status):
        return status


    def runstep(self,status):
        status.co2data.TempCo2EffectOnAMAX= status.co2data.Co2EffectOnAMAX
        status.co2data.TempCo2EffectOnEFF = status.co2data.Co2EffectOnEFF
        status.co2data.TempCo2EffectOnPotentialTraspiration = status.co2data.Co2EffectOnPotentialTraspiration

        status.co2data.Co2EffectOnAMAX = 1
        status.co2data.Co2EffectOnEFF = 1
        status.co2data.Co2EffectOnPotentialTraspiration = 1
        return status


    def integrate(self,status):
        return status


    def getinputslist(self):
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
