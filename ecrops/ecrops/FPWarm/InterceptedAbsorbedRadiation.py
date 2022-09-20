import copy
from math import exp


class InterceptedAbsorbedRadiation():
    """
    Intencepted absorbed radiation. Reference: Monsi, M., Saeki, T., 1953. Über den Lichtfaktor in den Pflanzengesellschaften und seine Bedeutung
    für die Stoffproduktion. Japanese Journal of Botany, 14, 22 - 52
    """

    def setparameters(self, container):
        return container

    def initialize(self, container):
        return container

    def integrate(self, container):
        return container

    def getparameterslist(self):
        return {

            "ExtinctionCoefficientSolarRadiation": {"Description": "Extinction coefficient for solar radiation",
                                                    "Type": "Number",
                                                    "Mandatory": "True", "UnitOfMeasure": "unitless"},
        }

    def runstep(self, container):

        try:
            ex = container.Weather[(container.day - container.first_day).days]  # get the meteo data for current day
            p = container.Parameters  # parameters
            s = container.States  # states
            s1 = container.States1  # ???
            a = container.Auxiliary  # ???
            r = container.Rates  # rates

            if (s.DevelopmentStageCode >= 1.00 and s.TotalLeafAreaIndex == 0):

                if (p.ExtinctionCoefficientSolarRadiation == 0):
                    s.GreenLeafAreaIndex = 0.03
                    s.TotalLeafAreaIndex = 0.03

            if (s.DevelopmentStageCode > 1 and s.DevelopmentStageCode <= 4):
                r.InterceptedSolarRadiationRate = self.LambertBeerLaw(p.ExtinctionCoefficientSolarRadiation,
                                                                      s.TotalLeafAreaIndex) * ex.GlobalSolarRadiation
                r.AbsorbedSolarRadiationRate = self.LambertBeerLaw(p.ExtinctionCoefficientSolarRadiation,
                                                                   s.GreenLeafAreaIndex) * ex.GlobalSolarRadiation

            else:
                r.InterceptedSolarRadiationRate = 0
                r.AbsorbedSolarRadiationRate = 0

            s1.InterceptedSolarRadiation = s.InterceptedSolarRadiation + r.InterceptedSolarRadiationRate
            s1.AbsorbedSolarRadiation = s.AbsorbedSolarRadiation + r.AbsorbedSolarRadiationRate


        except  Exception as e:
            print('Error in method runstep of class InterceptedAbsorbedRadiation:' + str(e))

        return container

    def LambertBeerLaw(self, coeff, GLAI):
        """Beer–Lambert law, empirically describing light intensity attenuation"""
        result = 1 - exp(-coeff * GLAI)

        return result
