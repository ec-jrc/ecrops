import copy
from ecrops.Printable import Printable
from math import exp
from ecrops.Step import Step

class PotentialTranspiration(Step):
    """
    Potential crop water transpiration. Reference: Stockle, C.O., Donatelli, M., Nelson, R., 2003. CropSyst, a cropping systems simulation model.
    European Journal of Agronomy, 18, 289-307
    """
    def setparameters(self, container):
        if not hasattr(container, 'WarmParameters'):
            from ecrops.Printable import Printable
            container.WarmParameters = Printable()
        container.WarmParameters.FullCanopyCoefficient = container.allparameters['FullCanopyCoefficient']
        container.WarmParameters.ExtinctionCoefficientSolarRadiation = container.allparameters['ExtinctionCoefficientSolarRadiation']

        return container

    def initialize(self, container):
        if not hasattr(container,'auxiliary'):
            container.auxiliary = Printable()
        container.auxiliary.DayOfPhysiologicalMaturity=0
        container.states.Transpiration = 0
        container.rates.TranspirationRate = 0
        return container

    def integrate(self, container):
        s = container.states  # states
        r = container.rates  # rates


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

            p = container.WarmParameters  # parameters
            s = container.states  # states
            r = container.rates  # rates
            a = container.auxiliary


            _kc = p.FullCanopyCoefficient

            if (s.DevelopmentStageCode >= 1 and s.DevelopmentStageCode <= 3):
                if (s.GreenLeafAreaIndex < 3):
                    if ((1 + (p.FullCanopyCoefficient - 1) * s.GreenLeafAreaIndex) > 0):
                        _kc = 1 + (p.FullCanopyCoefficient - 1) * s.GreenLeafAreaIndex / 3

                _TranspirationPotentialRate = _kc * container.weather.ET0 * \
                                              self.LambertBeerLaw(p.ExtinctionCoefficientSolarRadiation,
                                                                  s.GreenLeafAreaIndex)
                r.TranspirationRate = min(_TranspirationPotentialRate, r.WaterUptakeRate)

            else:
                r.TranspirationRate = 0

            if a.DayOfPhysiologicalMaturity > 1:
                r.TranspirationRate = 0

            s.Transpiration = s.Transpiration + r.TranspirationRate

            # move the s1 status to the states variable
            container.States = copy.deepcopy(s)

        except  Exception as e:
            print('Error in method runstep of class PotentialTranspiration:'+str(e))

        return container


    def LambertBeerLaw(self, coeff, GLAI):
        """LambertBeerLaw: empirically describing light intensity attenuation"""
        result = 1 - exp(-coeff * GLAI)

        return result

    def getinputslist(self):
        return {

            "DevelopmentStageCode": {"Description": "Development stage", "Type": "Number", "UnitOfMeasure": "unitless",
                                     "StatusVariable": "status.states.DevelopmentStageCode"},
            "GreenLeafAreaIndex": {"Description": "Green leaf area index",
                                   "Type": "Number", "UnitOfMeasure": "unitless",
                                   "StatusVariable": "status.states.GreenLeafAreaIndex"},
            "ET0": {"Description": "Canopy evapotranspiration",
                    "Type": "Number", "UnitOfMeasure": "cm",
                    "StatusVariable": "status.weather.ET0"},
            "WaterUptakeRate": {"Description": "Water uptake rate",
                    "Type": "Number", "UnitOfMeasure": "cm",
                    "StatusVariable": "status.rates.WaterUptakeRate"},
            "Transpiration": {"Description": "Transpiration ",
                              "Type": "Number", "UnitOfMeasure": "cm",
                              "StatusVariable": "status.states.Transpiration"},

        }

    def getoutputslist(self):
        return {
            "TranspirationRate": {"Description": "Transpiration rate",
                                "Type": "Number", "UnitOfMeasure": "cm",
                                "StatusVariable": "status.rates.TranspirationRate"},
            "Transpiration": {"Description": "Transpiration ",
                                  "Type": "Number", "UnitOfMeasure": "cm",
                                  "StatusVariable": "status.states.Transpiration"},
        }