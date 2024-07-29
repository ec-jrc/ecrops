from ecrops.Step import Step
class SenescenceRue(Step):
    """
    Senescence effect on radiation use efficiency.
    # Reference: Confalonieri, R., Gusberti, D., Acutis, M., 2006. Comparison of WOFOST, CropSyst and WARM for
    # simulating rice growth (Japonica type – short cycle varieties). Italian Journal of Agrometeorology, 3, 7-16
    """
    def setparameters(self, container):
        return container

    def initialize(self, container):
        container.states.RUESenescenceEffect = 0
        return container

    def integrate(self, container):

        s = container.states  # states
        r = container.rates  # rates

        return container

    def getparameterslist(self):
        return {}

    def runstep(self, container):

        try :

            s = container.states  # states
            r = container.rates  # rates

            if s.DevelopmentStageCode > 2 and s.DevelopmentStageCode <= 3:
                r.RUESenescenceEffectRate = 1.5 - 0.25 * s.DevelopmentStageCode

            else:
                r.RUESenescenceEffectRate = 1

            s.RUESenescenceEffect = s.RUESenescenceEffect + r.RUESenescenceEffectRate
        except  Exception as e:
            print('Error in method runstep of class SenescenceRue:'+str(e))

        return container


    def getinputslist(self):
        return {
            "DevelopmentStageCode": {"Description": "Development stage", "Type": "Number", "UnitOfMeasure": "unitless",
                                     "StatusVariable": "status.states.DevelopmentStageCode"},

            "RUESenescenceEffect": {"Description": "RUE senescence effect ",
                                    "Type": "Number",
                                    "UnitOfMeasure": "unitless",
                                    "StatusVariable": "status.states.RUESenescenceEffect"},

        }


    def getoutputslist(self):
        return {
            "RUESenescenceEffectRate": {"Description": "RUE senescence effect rate",
                                        "Type": "Number",
                                        "UnitOfMeasure": "unitless",
                                        "StatusVariable": "status.rates.RUESenescenceEffectRate"},
            "RUESenescenceEffect": {"Description": "RUE senescence effect ",
                                    "Type": "Number",
                                    "UnitOfMeasure": "unitless",
                                    "StatusVariable": "status.states.RUESenescenceEffect"},

        }
