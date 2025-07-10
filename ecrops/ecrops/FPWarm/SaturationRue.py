from ecrops.Step import Step
class SaturationRue(Step):
    """
    Saturation Rue step. Reference: Confalonieri, R., Gusberti, D., Acutis, M., 2006. Comparison of WOFOST, CropSyst and WARM for
    simulating rice growth (Japonica type – short cycle varieties). Italian Journal of Agrometeorology, 3, 7-16
    """
    def setparameters(self, container):
        if not hasattr(container, 'WarmParameters'):
            from ecrops.Printable import Printable
            container.WarmParameters = Printable()
        container.WarmParameters.ThresholdRadiationForSaturation = container.allparameters['ThresholdRadiationForSaturation']

        return container

    def initialize(self, container):
        container.states.RUESaturationEffect =0
        return container

    def integrate(self, container):
        s = container.states  # states

        r = container.rates  # rates

        return container

    def getparameterslist(self):
        return {
            "ThresholdRadiationForSaturation": {"Description": "Threshold  radiation for saturation",
                                           "Type": "Number",
                                           "Mandatory": "True", "UnitOfMeasure": "MJ"},
        }

    def runstep(self, container):

        try :

            p = container.WarmParameters  # parameters
            s = container.states  # states

            r = container.rates  # rates

            # Saturation of the enzymatic chains effect on radiation use efficiency.
            if container.weather.IRRAD >= p.ThresholdRadiationForSaturation:
                r.RUESaturationEffectRate = 2 - 0.04 *  container.weather.IRRAD
            else:
                r.RUESaturationEffectRate = 1

            s.RUESaturationEffect = s.RUESaturationEffect + r.RUESaturationEffectRate

        except  Exception as e:
            print('Error in method runstep of class SaturationRue:'+str(e))

        return container

    def getinputslist(self):
        return {


            "IRRAD": {"Description": "Daily shortwave radiation",
                      "Type": "Number", "UnitOfMeasure": "J/(m2 day) ",
                      "StatusVariable": "status.weather.IRRAD"},
            "RUESaturationEffect": {"Description": "RUE saturation effect ",
                                    "Type": "Number",
                                    "UnitOfMeasure": "unitless",
                                    "StatusVariable": "status.states.RUESaturationEffect"},

        }

    def getoutputslist(self):
        return {
            "RUESaturationEffectRate": {"Description": "RUE saturation effect rate",
                                   "Type": "Number",
                                   "UnitOfMeasure": "unitless",
                                   "StatusVariable": "status.rates.RUESaturationEffectRate"},
            "RUESaturationEffect": {"Description": "RUE saturation effect ",
                                        "Type": "Number",
                                        "UnitOfMeasure": "unitless",
                                        "StatusVariable": "status.states.RUESaturationEffect"},

        }
