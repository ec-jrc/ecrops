from math import exp

class PotentialWaterUptake():
    """
    Growing Degrees Days Temperature
    """
    def setparameters(self, container):
        return container

    def initialize(self, container):
        return container

    def integrate(self, container):
        return container

    def getparameterslist(self):
        return {
            "FullCanopyWaterUptakeMaximum": {"Description": "Full canopy water uptake maximum", "Type": "Number",
                                      "Mandatory": "True", "UnitOfMeasure": "kg m-2 d-1"},
            "ExtinctionCoefficientSolarRadiation": {"Description": "Extinction coefficient for solar radiation",
                                                    "Type": "Number",
                                                    "Mandatory": "True", "UnitOfMeasure": "unitless"},
        }

    def runstep(self, container):

        try :
            ex = container.Weather[(container.day - container.first_day).days]  # get the meteo data for current day
            p = container.Parameters  # parameters
            s = container.States  # states
            s1 = container.States1  # ???
            a = container.Auxiliary  # ???
            r = container.Rates  # rates

            if (s.DevelopmentStageCode > 1):
                r.WaterUptakeRate = p.FullCanopyWaterUptakeMaximum * \
                                    self.LambertBeerLaw(p.ExtinctionCoefficientSolarRadiation, s.GreenLeafAreaIndex)

            else:

                s1.WaterUptake = 0
                r.WaterUptakeRate = 0

            s1.WaterUptake = s.WaterUptake + r.WaterUptakeRate

        except  Exception as e:
            print('Error in method runstep of class PotentialWaterUptake:'+str(e))

        return container


    def LambertBeerLaw(self, coeff, GLAI):
        """LambertBeerLaw: empirically describing light intensity attenuation"""
        result = 1 - exp(-coeff * GLAI)

        return result