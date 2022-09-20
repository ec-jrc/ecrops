
class SaturationRue():
    """
    Saturation Rue step. Reference: Confalonieri, R., Gusberti, D., Acutis, M., 2006. Comparison of WOFOST, CropSyst and WARM for
    simulating rice growth (Japonica type – short cycle varieties). Italian Journal of Agrometeorology, 3, 7-16
    """
    def setparameters(self, container):
        return container

    def initialize(self, container):
        return container

    def integrate(self, container):
        return container

    def getparameterslist(self):
        return {
            "ThresholdRadiationForSaturation": {"Description": "Threshold  radiation for saturation",
                                           "Type": "Number",
                                           "Mandatory": "True", "UnitOfMeasure": "MJ"},
        }

    def runstep(self, container):

        try :
            ex = container.Weather[(container.day - container.first_day).days]  # get the meteo data for current day
            p = container.Parameters  # parameters
            s = container.States  # states
            s1 = container.States1  # ???
            a = container.Auxiliary  # ???
            r = container.Rates  # rates

            # Saturation of the enzymatic chains effect on radiation use efficiency.
            if ex.GlobalSolarRadiation >= p.ThresholdRadiationForSaturation:
                r.RUESaturationEffectRate = 2 - 0.04 * ex.GlobalSolarRadiation
            else:
                r.RUESaturationEffectRate = 1

            s1.RUESaturationEffect = s.RUESaturationEffect + r.RUESaturationEffectRate

        except  Exception as e:
            print('Error in method runstep of class SaturationRue:'+str(e))

        return container