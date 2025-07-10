from ecrops.Step import Step
import math


class HeatInducedSterilityWARM(Step):
    """
    HeatInducedSterilityWARM
    """

    def setparameters(self, container):
        if not hasattr(container,'WarmParameters'):
            from ecrops.Printable import Printable
            container.WarmParameters=Printable()
        container.WarmParameters.ThresholdTemperatureInducingHeatSterility = container.allparameters['ThresholdTemperatureInducingHeatSterility']
        container.WarmParameters.SensitivityToHeatShockInducedSterility = container.allparameters['SensitivityToHeatShockInducedSterility']


        return container

    def initialize(self, container):
        self.HighSensitivityForManyDays=True
        container.states.HeatInducedSpikeletSterilityState=0
        return container

    def integrate(self, container):
        s = container.states  # states
        r = container.rates  # rates

        return container

    def getparameterslist(self):
        return {
            "ThresholdTemperatureInducingHeatSterility": {"Description": "ThresholdTemperatureInducingHeatSterility", "Type": "Number",
                                              "Mandatory": "True", "UnitOfMeasure": ""},
            "SensitivityToHeatShockInducedSterility": {"Description": "SensitivityToHeatShockInducedSterility", "Type": "Number",
                                                          "Mandatory": "True", "UnitOfMeasure": ""},

        }

    def getinputslist(self):
        return {

            "DevelopmentStageCode": {"Description": "Development stage", "Type": "Number", "UnitOfMeasure": "unitless",
                                     "StatusVariable": "status.states.DevelopmentStageCode"},
            "TEMP_MIN": {"Description": "Minimum temperature",
                         "Type": "Number", "UnitOfMeasure": "C",
                         "StatusVariable": "status.weather.TEMP_MIN"},
            "TEMP_MAX": {"Description": "Maximum temperature",
                         "Type": "Number", "UnitOfMeasure": "C",
                         "StatusVariable": "status.weather.TEMP_MAX"},
            "HeatInducedSpikeletSterilityState": {"Description": "Heat induced spikelet sterility",
                                                  "Type": "Number",
                                                  "UnitOfMeasure": "unitless",
                                                  "StatusVariable": "status.states.HeatInducedSpikeletSterilityState"},

        }

    def getoutputslist(self):
        return {
            "HeatInducedSpikeletSterilityRate": {"Description": "Heat induced spikelet sterility rate",
                                                 "Type": "Number",
                                                 "UnitOfMeasure": "unitless",
                                                 "StatusVariable": "status.rates.HeatInducedSpikeletSterilityRate"},
            "HeatInducedSpikeletSterilityState": {"Description": "Heat induced spikelet sterility",
                                                 "Type": "Number",
                                                 "UnitOfMeasure": "unitless",
                                                 "StatusVariable": "status.states.HeatInducedSpikeletSterilityState"},


        }

    def runstep(self, container):
        """

        """

        p = container.WarmParameters  # parameters
        s = container.states  # states
        r = container.rates  # rates

        try:
            DailyStress = 0

            if s.DevelopmentStageCode >= 1.9 and s.DevelopmentStageCode <= 2.1:


                Tavg =  (container.weather.TEMP_MAX+container.weather.TEMP_MIN) / 2
                DT = container.weather.TEMP_MAX - container.weather.TEMP_MIN

                #Strategy to estimate hourly air temperature.  agronomy@isci.it, February 2008. Campbell, G.S. 1985. Soil physics with BASIC: transport models for soil-plant systems.
	            #HAT Campbell
                HourlyTemperatureMeristematicApex = []
                CampbellTimingVariation = 15
                for j in range(24):
                    HourlyTemperatureMeristematicApex.append( Tavg + DT / 2 * math.cos(0.2618 * (j - CampbellTimingVariation)))


                for j in range(24):

                    DailyStress = DailyStress +  self.HourlySterilityFactor(HourlyTemperatureMeristematicApex[j], p.ThresholdTemperatureInducingHeatSterility)

                if (self.HighSensitivityForManyDays == False):

                    Delta = 0.06
                    Sigma = Delta / 2.5

                else:
                    Delta = 0.125
                    Sigma = Delta / 2.5



                DevelopmentStageCodeExactlyBetweenPanicleInitiationAndHeading = 2



                r.HeatInducedSpikeletSterilityRate = p.SensitivityToHeatShockInducedSterility * DailyStress * self.BellFactor(s.DevelopmentStageCode, DevelopmentStageCodeExactlyBetweenPanicleInitiationAndHeading,                    Sigma, Delta) / 100;


            else:

                r.HeatInducedSpikeletSterilityRate = 0


            s.HeatInducedSpikeletSterilityState = s.HeatInducedSpikeletSterilityState + r.HeatInducedSpikeletSterilityRate

            if (s.HeatInducedSpikeletSterilityState > 1):
                s.HeatInducedSpikeletSterilityState = 1



        except  Exception as e:
            print('Error in method runstep of class HeatInducedSterilityWARM:' + str(e))

        return container


    def BellFactor(self, DVS, DVSmiddle, Sigma, Delta):


        if (DVS >= 1.9 and DVS <= 2.1):


            F1 = Delta / (Sigma * (math.pow((2 * math.pi), 0.5)))

            expo = -((math.pow((DVS - DVSmiddle), 2)) / (2 * (math.pow(Sigma, 2))))

            F2 = math.exp(expo)
            result = F1 * F2

        else:

            result = 0

        return result


    def HourlySterilityFactor( self,  Thour,     ThresholdT):

        if (Thour < ThresholdT):

            result = 0

        else:

            result = Thour - ThresholdT

        return result


