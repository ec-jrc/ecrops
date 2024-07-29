from ecrops.wofost_util.util import isC3crop
from ..Printable import Printable
from ecrops.Step import Step

class Co2Data(Step):
    """This step calculates the CO2 effect on plant, starting from input parameters Co2FertSlope and Co2FertReference"""

    def getparameterslist(self):
        return {
            "Co2FertSlope": {"Description": "Slope of the linear CO2 fertilization function", "Type": "Number",
                             "Mandatory": "True",
                             "UnitOfMeasure": "unitless"},
            "Co2FertReference": {"Description": "Intercept of the linear CO2 fertilization function", "Type": "Number",
                                 "Mandatory": "True",
                                 "UnitOfMeasure": "unitless"},
            "ConsiderCo2Effect": {"Description": "Set to true to consider the effect of the CO2 in the crop simulation",
                                  "Type": "Boolean",
                                  "Mandatory": "True",
                                  "UnitOfMeasure": "unitless"}

        }

    def setparameters(self, status):
        return status

    def runstep(self, status):
        return status

    def initialize(self, status):
        status.co2data = Printable()

        if status.ConsiderCo2Effect == True:

            if isC3crop(status.crop):
                status.co2data.Co2EffectOnAMAX = (
                            1 + status.Co2FertSlope * (status.Co2Concentration - status.Co2FertReference) / 100)
                status.co2data.Co2EffectOnEFF = (1 + 0.11 * (status.Co2Concentration - status.Co2FertReference) / 355)
                status.co2data.Co2EffectOnPotentialTraspiration = (
                            1 - 0.10 * (status.Co2Concentration - status.Co2FertReference) / 355)
            else:
                status.co2data.Co2EffectOnAMAX = 1
                status.co2data.Co2EffectOnEFF = 1
                status.co2data.Co2EffectOnPotentialTraspiration = (
                            1 - 0.26 * (status.Co2Concentration - status.Co2FertReference) / 355);

        else:
            status.co2data.Co2EffectOnAMAX = 1
            status.co2data.Co2EffectOnEFF = 1
            status.co2data.Co2EffectOnPotentialTraspiration = 1

        return self.runstep(status)

    def integrate(self, status):
        return status

    def getinputslist(self):
        return {

            "Co2Concentration": {"Description": "Co2 concentration",
                                "Type": "Number", "UnitOfMeasure": "ppm",
                                "StatusVariable": "status.Co2Concentration"},
            "Co2FertReference": {"Description": "Co2 reference",
                               "Type": "Number", "UnitOfMeasure": "ppm",
                               "StatusVariable": "status.Co2FertReference"},
            "crop": {"Description": "Crop code",
                                                 "Type": "Number", "UnitOfMeasure": "unitless",
                                                 "StatusVariable": "status.crop"},
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


        }
