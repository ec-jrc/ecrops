from math import exp
from ecrops.Step import Step

class PotentialWaterUptake(Step):
    """
    Growing Degrees Days Temperature
    """
    def setparameters(self, container):
        container.WarmParameters.FullCanopyWaterUptakeMaximum = container.allparameters['FullCanopyWaterUptakeMaximum']
        container.WarmParameters.ExtinctionCoefficientSolarRadiation = container.allparameters['ExtinctionCoefficientSolarRadiation']

        return container

    def initialize(self, container):
        container.states.WaterUptake = 0
        return container

    def integrate(self, container):
        s = container.states  # states
        r = container.rates  # rates


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

            p = container.WarmParameters  # parameters
            s = container.states  # states
            r = container.rates  # rates

            if (s.DevelopmentStageCode > 1):
                r.WaterUptakeRate = p.FullCanopyWaterUptakeMaximum * \
                                    self.LambertBeerLaw(p.ExtinctionCoefficientSolarRadiation, s.GreenLeafAreaIndex)

            else:

                s.WaterUptake = 0
                r.WaterUptakeRate = 0
            s.WaterUptake = s.WaterUptake + r.WaterUptakeRate


        except  Exception as e:
            print('Error in method runstep of class PotentialWaterUptake:'+str(e))

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


            "WaterUptake": {"Description": "Water uptake ",
                            "Type": "Number", "UnitOfMeasure": "cm",
                            "StatusVariable": "status.states.WaterUptake"},
        }

    def getoutputslist(self):
        return {
             "WaterUptakeRate": {"Description": "Water uptake rate",
                                "Type": "Number", "UnitOfMeasure": "cm",
                                "StatusVariable": "status.rates.WaterUptakeRate"},
            "WaterUptake": {"Description": "Water uptake ",
                                "Type": "Number", "UnitOfMeasure": "cm",
                                "StatusVariable": "status.states.WaterUptake"},
        }