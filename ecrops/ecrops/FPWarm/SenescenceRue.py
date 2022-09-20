
class SenescenceRue:
    """
    Senescence effect on radiation use efficiency.
    # Reference: Confalonieri, R., Gusberti, D., Acutis, M., 2006. Comparison of WOFOST, CropSyst and WARM for
    # simulating rice growth (Japonica type – short cycle varieties). Italian Journal of Agrometeorology, 3, 7-16
    """
    def setparameters(self, container):
        return container

    def initialize(self, container):
        return container

    def integrate(self, container):
        return container

    def getparameterslist(self):
        return {}

    def runstep(self, container):

        try :
            ex = container.Weather[(container.day - container.first_day).days]  # get the meteo data for current day
            p = container.Parameters  # parameters
            s = container.States  # states
            s1 = container.States1  # ???
            a = container.Auxiliary  # ???
            r = container.Rates  # rates

            if s.DevelopmentStageCode > 2 and s.DevelopmentStageCode <= 3:
                r.RUESenescenceEffectRate = 1.5 - 0.25 * s.DevelopmentStageCode

            else:
                r.RUESenescenceEffectRate = 1

            s1.RUESenescenceEffect = s.RUESenescenceEffect + r.RUESenescenceEffectRate


        except  Exception as e:
            print('Error in method runstep of class SenescenceRue:'+str(e))

        return container


