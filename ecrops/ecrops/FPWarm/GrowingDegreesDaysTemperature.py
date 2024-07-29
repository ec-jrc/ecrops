from ecrops.Step import Step
class GrowingDegreesDaysTemperature(Step):
    """Growing Degrees Days Temperature"""

    def setparameters(self, container):
        container.WarmParameters.BaseTemperatureDevelopment = container.allparameters['BaseTemperatureDevelopment']
        container.WarmParameters.CutoffTemperatureDevelopment = container.allparameters['CutoffTemperatureDevelopment']

        return container

    def initialize(self, container):
        container.states.GrowingDegreeDaysTemperature=0
        return container

    def integrate(self, container):
        s = container.states  # states

        r = container.rates  # rates

        return container

    def getparameterslist(self):
        return {
            "BaseTemperatureDevelopment": {"Description": "Base temperature for development", "Type": "Number",
                                           "Mandatory": "True", "UnitOfMeasure": "C"},
            "CutoffTemperatureDevelopment": {"Description": "Cutoff temperature for development", "Type": "Number",
                                             "Mandatory": "True", "UnitOfMeasure": "C"},
        }

    def getinputslist(self):
        return {

            "DevelopmentStageCode": {"Description": "Development stage", "Type": "Number", "UnitOfMeasure": "unitless",
                                     "StatusVariable": "status.states.DevelopmentStageCode"},
            "TEMP": {"Description": "Average daily temperature",
                     "Type": "Number", "UnitOfMeasure": "C",
                     "StatusVariable": "status.weather.TEMP"},
            "ColdInducedSpikeletSterilityState": {"Description": "Cold induced spikelet sterility",
                                                  "Type": "Number",
                                                  "UnitOfMeasure": "unitless",
                                                  "StatusVariable": "status.states.ColdInducedSpikeletSterilityState"},

            "GrowingDegreeDaysTemperature": {"Description": "Growing degree days by temperature",
                                             "Type": "Number",
                                             "UnitOfMeasure": "C",
                                             "StatusVariable": "status.states.GrowingDegreeDaysTemperature"},
        }

    def getoutputslist(self):
        return {
            "GrowingDegreeDaysTemperatureRate": {"Description": "Growing degree days by temperature rate",
                                                 "Type": "Number",
                                                 "UnitOfMeasure": "C",
                                                 "StatusVariable": "status.rates.GrowingDegreeDaysTemperatureRate"},

            "GrowingDegreeDaysTemperature": {"Description": "Growing degree days by temperature",
                                                 "Type": "Number",
                                                 "UnitOfMeasure": "C",
                                                 "StatusVariable": "status.states.GrowingDegreeDaysTemperature"},
        }

    def runstep(self, container):

        try:

            p = container.WarmParameters  # parameters
            s = container.states  # states

            r = container.rates  # rates

            Tavg = container.weather.TEMP

            if Tavg <= p.BaseTemperatureDevelopment:
                r.GrowingDegreeDaysTemperatureRate = 0

            else:
                if Tavg >= p.CutoffTemperatureDevelopment:
                    r.GrowingDegreeDaysTemperatureRate = p.CutoffTemperatureDevelopment - p.BaseTemperatureDevelopment
                else:
                    r.GrowingDegreeDaysTemperatureRate = Tavg - p.BaseTemperatureDevelopment

            s.GrowingDegreeDaysTemperature = s.GrowingDegreeDaysTemperature + r.GrowingDegreeDaysTemperatureRate
        except Exception as e:
            print('Error in method runstep of class GrowingDegreesDAysTemperature:' + str(e))

        return container
