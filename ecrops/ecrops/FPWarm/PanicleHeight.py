
class PanicleHeight:
    """
    PANICLE HEIGHT. Reference: Confalonieri, R., Mariani, L., Bocchi, S., 2004. PREDA: a prototype of a rice cold damage early
    warning system at high latitudes. Proceedings of the International Rice Cold Tolerance Workshop, Canberra, Australia, 22-23 July 2004
    """
    def setparameters(self, container):
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

    def runstep(self, container):

        try :
            ex = container.Weather[(container.day - container.first_day).days]  # get the meteo data for current day
            p = container.Parameters  # parameters
            s = container.States  # states
            s1 = container.States1  # ???
            a = container.Auxiliary  # ???
            r = container.Rates  # rates

            if s.DevelopmentStageCode >= 1.6 and s.DevelopmentStageCode <= 2:
                dvsC = s.DevelopmentStageCode - 1
                F1 = (dvsC - 0.6) / (1 - 0.6)
                F2 = (2 - dvsC) / 1
                Expo = 1 / (1 - 0.6)
                s1.PanicleHeight = ((F1 * (F2 ** Expo)) ** 5) * p.MaximumPanicleHeight

            else:
                if s1.DevelopmentStageCode > 2:
                    s1.PanicleHeight = p.MaximumPanicleHeight
                else:
                    s1.PanicleHeight = 0

        except  Exception as e:
            print('Error in method runstep of class PanicleHeight:'+str(e))

        return container