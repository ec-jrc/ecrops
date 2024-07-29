from ecrops.Step import Step
import copy
from math import exp


class InterceptedAbsorbedRadiation(Step):
    """
    Intencepted absorbed radiation. Reference: Monsi, M., Saeki, T., 1953. Über den Lichtfaktor in den Pflanzengesellschaften und seine Bedeutung
    für die Stoffproduktion. Japanese Journal of Botany, 14, 22 - 52
    """

    def setparameters(self, container):
        container.WarmParameters.ExtinctionCoefficientSolarRadiation = container.allparameters['ExtinctionCoefficientSolarRadiation']

        return container

    def initialize(self, container):
        container.states.InterceptedSolarRadiation = 0
        container.states.AbsorbedSolarRadiation = 0


        return container

    def integrate(self, container):
        s = container.states  # states
        r = container.rates  # rates

        return container

    def getparameterslist(self):
        return {

            "ExtinctionCoefficientSolarRadiation": {"Description": "Extinction coefficient for solar radiation",
                                                    "Type": "Number",
                                                    "Mandatory": "True", "UnitOfMeasure": "unitless"},
        }

    def getinputslist(self):
        return {

            "DevelopmentStageCode": {"Description": "Development stage", "Type": "Number", "UnitOfMeasure": "unitless",
                                     "StatusVariable": "status.states.DevelopmentStageCode"},
            "IRRAD": {"Description": "Daily shortwave radiation",
                      "Type": "Number", "UnitOfMeasure": "J/(m2 day) ",
                      "StatusVariable": "status.weather.IRRAD"},
            "TotalLeafAreaIndex": {"Description": "Total leaf area index",
                                                  "Type": "Number",
                                                  "UnitOfMeasure": "unitless",
                                                  "StatusVariable": "status.states.TotalLeafAreaIndex"},
            "InterceptedSolarRadiation": {"Description": "Intercepted solar radiation ",
                                          "Type": "Number",
                                          "UnitOfMeasure": "unitless",
                                          "StatusVariable": "status.states.InterceptedSolarRadiation"},
            "AbsorbedSolarRadiation": {"Description": "Absorbed solar radiation ",
                                       "Type": "Number",
                                       "UnitOfMeasure": "unitless",
                                       "StatusVariable": "status.states.AbsorbedSolarRadiation"},

        }

    def getoutputslist(self):
        return {
            "TotalLeafAreaIndex": {"Description": "Total leaf area index",
                                   "Type": "Number",
                                   "UnitOfMeasure": "unitless",
                                   "StatusVariable": "status.states.TotalLeafAreaIndex"},
            "GreenLeafAreaIndex": {"Description": "Green leaf area index",
                                   "Type": "Number",
                                   "UnitOfMeasure": "unitless",
                                   "StatusVariable": "status.states.GreenLeafAreaIndex"},
            "InterceptedSolarRadiationRate": {"Description": "Intercepted solar radiation rate",
                                   "Type": "Number",
                                   "UnitOfMeasure": "unitless",
                                   "StatusVariable": "status.rates.InterceptedSolarRadiationRate"},
            "AbsorbedSolarRadiationRate": {"Description": "Absorbed solar radiation rate",
                                              "Type": "Number",
                                              "UnitOfMeasure": "unitless",
                                              "StatusVariable": "status.rates.AbsorbedSolarRadiationRate"},
            "InterceptedSolarRadiation": {"Description": "Intercepted solar radiation ",
                                              "Type": "Number",
                                              "UnitOfMeasure": "unitless",
                                              "StatusVariable": "status.states.InterceptedSolarRadiation"},
            "AbsorbedSolarRadiation": {"Description": "Absorbed solar radiation ",
                                           "Type": "Number",
                                           "UnitOfMeasure": "unitless",
                                           "StatusVariable": "status.states.AbsorbedSolarRadiation"},

        }

    def runstep(self, container):

        try:

            p = container.WarmParameters  # parameters
            s = container.states  # states
            r = container.rates  # rates


            #initalization of LAU at emergence
            if (s.DevelopmentStageCode >= 1.00 and s.TotalLeafAreaIndex == 0):
                s.GreenLeafAreaIndex = 0.007
                s.TotalLeafAreaIndex = 0.007

            if (s.DevelopmentStageCode > 1 and s.DevelopmentStageCode <= 4):
                r.InterceptedSolarRadiationRate = self.LambertBeerLaw(p.ExtinctionCoefficientSolarRadiation,
                                                                      s.TotalLeafAreaIndex) * container.weather.IRRAD
                r.AbsorbedSolarRadiationRate = self.LambertBeerLaw(p.ExtinctionCoefficientSolarRadiation,
                                                                   s.GreenLeafAreaIndex) * container.weather.IRRAD

            else:
                r.InterceptedSolarRadiationRate = 0
                r.AbsorbedSolarRadiationRate = 0

            s.InterceptedSolarRadiation = s.InterceptedSolarRadiation + r.InterceptedSolarRadiationRate
            s.AbsorbedSolarRadiation = s.AbsorbedSolarRadiation + r.AbsorbedSolarRadiationRate

        except  Exception as e:
            print('Error in method runstep of class InterceptedAbsorbedRadiation:' + str(e))

        return container

    def LambertBeerLaw(self, coeff, GLAI):
        """Beer–Lambert law, empirically describing light intensity attenuation"""
        result = 1 - exp(-coeff * GLAI)

        return result
