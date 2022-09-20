class GrowingDegreesDaysTemperature():
    """Growing Degrees Days Temperature"""

    def setparameters(self, container):
        return container

    def initialize(self, container):
        return container

    def integrate(self, container):
        return container

    def getparameterslist(self):
        return {
            "BaseTemperatureDevelopment": {"Description": "Base temperature for development", "Type": "Number",
                                           "Mandatory": "True", "UnitOfMeasure": "C"},
            "CutoffTemperatureDevelopment": {"Description": "Cutoff temperature for development", "Type": "Number",
                                             "Mandatory": "True", "UnitOfMeasure": "C"},
        }

    def runstep(self, container):

        try:
            ex = container.Weather[(container.day - container.first_day).days]  # get the meteo data for current day
            p = container.Parameters  # parameters
            s = container.States  # states
            s1 = container.States1  # ???
            a = container.Auxiliary  # ???
            r = container.Rates  # rates

            Tavg = ex.AirTemperatureAverage

            if Tavg <= p.BaseTemperatureDevelopment:
                r.GrowingDegreeDaysTemperatureRate = 0

            else:
                if Tavg >= p.CutoffTemperatureDevelopment:
                    r.GrowingDegreeDaysTemperatureRate = p.CutoffTemperatureDevelopment - p.BaseTemperatureDevelopment
                else:
                    r.GrowingDegreeDaysTemperatureRate = Tavg - p.BaseTemperatureDevelopment

            s1.GrowingDegreeDaysTemperature = s.GrowingDegreeDaysTemperature + r.GrowingDegreeDaysTemperatureRate


        except Exception as e:
            print('Error in method runstep of class GrowingDegreesDAysTemperature:' + str(e))

        return container
