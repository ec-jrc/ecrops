from ecrops.Step import Step
class PanicleHeight(Step):
    """
    PANICLE HEIGHT. Reference: Confalonieri, R., Mariani, L., Bocchi, S., 2004. PREDA: a prototype of a rice cold damage early
    warning system at high latitudes. Proceedings of the International Rice Cold Tolerance Workshop, Canberra, Australia, 22-23 July 2004
    """
    def setparameters(self, container):
        container.WarmParameters.MaximumPanicleHeight = container.allparameters['MaximumPanicleHeight']

        return container

    def initialize(self, container):
        return container

    def integrate(self, container):
        return container

    def getparameterslist(self):
        return {
            "MaximumPanicleHeight": {"Description": "Max panicle height",
                             "Type": "Number",
                             "Mandatory": "True", "UnitOfMeasure": "cm"},
        }

    def getinputslist(self):
        return {

            "DevelopmentStageCode": {"Description": "Development stage", "Type": "Number", "UnitOfMeasure": "unitless",
                                     "StatusVariable": "status.states.DevelopmentStageCode"},

        }

    def getoutputslist(self):
        return {
            "PanicleHeight": {"Description": "Panicle height",
                                                 "Type": "Number",
                                                 "UnitOfMeasure": "cm",
                                                 "StatusVariable": "status.states.PanicleHeight"},


        }
    def runstep(self, container):

        try :

            p = container.WarmParameters  # parameters
            s = container.states  # states
            r = container.rates  # rates

            if s.DevelopmentStageCode >= 1.6 and s.DevelopmentStageCode <= 2:
                dvsC = s.DevelopmentStageCode - 1
                F1 = (dvsC - 0.6) / (1 - 0.6)
                F2 = (2 - dvsC) / 1
                Expo = 1 / (1 - 0.6)
                s.PanicleHeight = ((F1 * (F2 ** Expo)) ** 5) * p.MaximumPanicleHeight

            else:
                if s.DevelopmentStageCode > 2:
                    s.PanicleHeight = p.MaximumPanicleHeight
                else:
                    s.PanicleHeight = 0

        except  Exception as e:
            print('Error in method runstep of class PanicleHeight:'+str(e))

        return container