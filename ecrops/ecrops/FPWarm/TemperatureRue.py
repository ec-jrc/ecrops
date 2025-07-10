from ecrops.Step import Step
class TemperatureRue(Step):
    """
    Temperature effect on radiation use efficiency.
    Reference: Yin, X., Kropff, M.J., McLaren, G., Visperas, R.M., 1995. A nonlinear model for crop development
    as a function of temperature. Agricultural and Forest Meteorology, 77, 1-16
    """
    def setparameters(self, container):
        if not hasattr(container, 'WarmParameters'):
            from ecrops.Printable import Printable
            container.WarmParameters = Printable()
        container.WarmParameters.BaseTemperatureForGrowth = container.allparameters['BaseTemperatureForGrowth']
        container.WarmParameters.OptimumTemperatureForGrowth = container.allparameters['OptimumTemperatureForGrowth']
        container.WarmParameters.MaximumTemperatureForGrowth = container.allparameters['MaximumTemperatureForGrowth']
        container.WarmParameters.BetaFunctionCShapeParameter = container.allparameters['BetaFunctionCShapeParameter']


        return container

    def initialize(self, container):
        container.states.RUETemperatureEffect = 0
        return container

    def integrate(self, container):
        s = container.states  # states
        r = container.rates  # rates


        return container

    def getparameterslist(self):
        return {
            "BetaFunctionCShapeParameter": {"Description": "BetaFunctionCShapeParameter",
                                         "Type": "Number",
                                         "Mandatory": "True", "UnitOfMeasure": ""},
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

    def getinputslist(self):
        return {

            "TEMP": {"Description": "Average daily temperature",
                     "Type": "Number", "UnitOfMeasure": "C",
                     "StatusVariable": "status.weather.TEMP"},
            "RUETemperatureEffect": {"Description": "RUE Temperature Effect ", "Type": "Number",
                                     "UnitOfMeasure": "",
                                     "StatusVariable": "status.states.RUETemperatureEffect"},
        }

    def getoutputslist(self):
        return {
            "RUETemperatureEffectRate": {"Description": "RUE Temperature Effect Rate", "Type": "Number",
                                         "UnitOfMeasure": "",
                                         "StatusVariable": "status.rates.RUETemperatureEffectRate"},
            "RUETemperatureEffect": {"Description": "RUE Temperature Effect ", "Type": "Number",
                                         "UnitOfMeasure": "",
                                         "StatusVariable": "status.states.RUETemperatureEffect"},
        }
    def runstep(self, container):

        try :

            p = container.WarmParameters  # parameters
            s = container.states  # states
            r = container.rates  # rates

            Tavg = container.weather.TEMP
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
            s.RUETemperatureEffect = s.RUETemperatureEffect + r.RUETemperatureEffectRate

        except  Exception as e:
            print('Error in method runstep of class Temperature:'+str(e))

        return container