
class TemperatureRue:
    """
    Temperature effect on radiation use efficiency.
    Reference: Yin, X., Kropff, M.J., McLaren, G., Visperas, R.M., 1995. A nonlinear model for crop development
    as a function of temperature. Agricultural and Forest Meteorology, 77, 1-16
    """
    def setparameters(self, container):
        return container

    def initialize(self, container):
        return container

    def integrate(self, container):
        return container

    def getparameterslist(self):
        return {
            "BaseTemperatureForGrowth": {"Description": "Base temperature for growth",
                                            "Type": "Number",
                                            "Mandatory": "True", "UnitOfMeasure": "C"},
            "OptimumTemperatureForGrowth": {"Description": "Optimum temperature for growth",
                                            "Type": "Number",
                                            "Mandatory": "True", "UnitOfMeasure": "C"},
            "MaximumTemperatureForGrowth": {"Description": "Maximum temperature for growth",
                                            "Type": "Number",
                                            "Mandatory": "True", "UnitOfMeasure": "C"},
        }

    def runstep(self, container):

        try :
            ex = container.Weather[(container.day - container.first_day).days]  # get the meteo data for current day
            p = container.Parameters  # parameters
            s = container.States  # states
            s1 = container.States1  # ???
            a = container.Auxiliary  # ???
            r = container.Rates  # rates

            Tavg = ex.AirTemperatureAverage
            if Tavg > p.OptimumTemperatureForGrowth:
                Tavg = p.OptimumTemperatureForGrowth

            Espo = float(p.MaximumTemperatureForGrowth - p.OptimumTemperatureForGrowth) / \
                   float(p.OptimumTemperatureForGrowth - p.BaseTemperatureForGrowth)

            FirstFactor = float(Tavg - p.BaseTemperatureForGrowth) / \
                          float(p.OptimumTemperatureForGrowth - p.BaseTemperatureForGrowth)

            SecondFactor = float(p.MaximumTemperatureForGrowth - Tavg) / \
                           float(p.MaximumTemperatureForGrowth - p.OptimumTemperatureForGrowth)

            if FirstFactor < 0:
                FirstFactor = 0

            if SecondFactor < 0:
                SecondFactor = 0

            r.RUETemperatureEffectRate = (FirstFactor * (SecondFactor ** Espo)) ** p.BetaFunctionCShapeParameter
            s1.RUETemperatureEffect = s.RUETemperatureEffect + r.RUETemperatureEffectRate

        except  Exception as e:
            print('Error in method runstep of class Temperature:'+str(e))

        return container