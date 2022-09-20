import copy
from math import exp


class PotentialTranspiration():
    """
    Potential crop water transpiration. Reference: Stockle, C.O., Donatelli, M., Nelson, R., 2003. CropSyst, a cropping systems simulation model.
    European Journal of Agronomy, 18, 289-307
    """
    def setparameters(self, container):
        return container

    def initialize(self, container):
        return container

    def integrate(self, container):
        return container

    def getparameterslist(self):
        return {
            "FullCanopyCoefficient": {"Description": "Full canopy coefficient", "Type": "Number",
                                                "Mandatory": "True", "UnitOfMeasure": "unitess"},
            "ExtinctionCoefficientSolarRadiation": {"Description": "Extinction coefficient for solar radiation", "Type": "Number",
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

            _kc = p.FullCanopyCoefficient

            if (s.DevelopmentStageCode >= 1 and s.DevelopmentStageCode <= 3):
                if (s.GreenLeafAreaIndex < 3):
                    if ((1 + (p.FullCanopyCoefficient - 1) * s.GreenLeafAreaIndex) > 0):
                        _kc = 1 + (p.FullCanopyCoefficient - 1) * s.GreenLeafAreaIndex / 3

                _TranspirationPotentialRate = _kc * ex.ReferenceEvapotranspiration * \
                                              self.LambertBeerLaw(p.ExtinctionCoefficientSolarRadiation,
                                                                  s.GreenLeafAreaIndex)
                r.TranspirationRate = min(_TranspirationPotentialRate, r.WaterUptakeRate)

            else:
                r.TranspirationRate = 0

            if a.DayOfPhysiologicalMaturity > 1:
                r.TranspirationRate = 0

            s1.Transpiration = s.Transpiration + r.TranspirationRate

            # move the s1 status to the states variable
            container.States = copy.deepcopy(s1)

        except  Exception as e:
            print('Error in method runstep of class PotentialTranspiration:'+str(e))

        return container


    def LambertBeerLaw(self, coeff, GLAI):
        """LambertBeerLaw: empirically describing light intensity attenuation"""
        result = 1 - exp(-coeff * GLAI)

        return result