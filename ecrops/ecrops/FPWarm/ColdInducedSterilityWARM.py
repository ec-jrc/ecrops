from ecrops.Step import Step
import math


class ColdInducedSterilityWARM(Step):
    """
    ColdInducedSterilityWARM
    """

    def setparameters(self, container):
        if not hasattr(container, 'WarmParameters'):
            from ecrops.Printable import Printable
            container.WarmParameters = Printable()
        container.WarmParameters.ThresholdTemperatureInducingSterilityBeforeFlowering = container.allparameters['ThresholdTemperatureInducingSterilityBeforeFlowering']
        container.WarmParameters.ThresholdTemperatureInducingSterilityDuringFlowering = container.allparameters['ThresholdTemperatureInducingSterilityDuringFlowering']
        container.WarmParameters.SensitivityToColdShockInducedSterility = container.allparameters['SensitivityToColdShockInducedSterility']

        return container

    def initialize(self, container):
        self.HighSensitivityForManyDays = True
        container.states.ColdInducedSpikeletSterilityState = 0
        container.rates.ColdInducedSpikeletSterilityRate = 0
        return container

    def integrate(self, container):
        s = container.states  # states
        r = container.rates  # rates

        return container

    def getparameterslist(self):
        return {
            "ThresholdTemperatureInducingSterilityDuringFlowering": {"Description": "ThresholdTemperatureInducingSterilityDuringFlowering", "Type": "Number",
                                                                     "Mandatory": "True", "UnitOfMeasure": ""},
            "ThresholdTemperatureInducingSterilityBeforeFlowering": {"Description": "ThresholdTemperatureInducingSterilityBeforeFlowering", "Type": "Number",
                                                                     "Mandatory": "True", "UnitOfMeasure": ""},
            "SensitivityToColdShockInducedSterility": {"Description": "SensitivityToColdShockInducedSterility", "Type": "Number",
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
            "ColdInducedSpikeletSterilityState": {"Description": "Cold induced spikelet sterility",
                                                  "Type": "Number",
                                                  "UnitOfMeasure": "unitless",
                                                  "StatusVariable": "status.states.ColdInducedSpikeletSterilityState"},

        }

    def getoutputslist(self):
        return {
            "ColdInducedSpikeletSterilityRate": {"Description": "Cold induced spikelet sterility rate", "Type": "Number",
                                                 "UnitOfMeasure": "unitless",
                                                 "StatusVariable": "status.rates.ColdInducedSpikeletSterilityRate"},
            "ColdInducedSpikeletSterilityState": {"Description": "Cold induced spikelet sterility",
                                                  "Type": "Number",
                                                  "UnitOfMeasure": "unitless",
                                                  "StatusVariable": "status.states.ColdInducedSpikeletSterilityState"},

        }

    def runstep(self, container):
        """

        """

        try:

            p = container.WarmParameters  # parameters
            s = container.states  # states
            r = container.rates  # rates


            DailyStress = 0;

            if s.DevelopmentStageCode >= 1.6 and s.DevelopmentStageCode <= 1.9:

                Tavg = (container.weather.TEMP_MAX + container.weather.TEMP_MIN) / 2
                DT = container.weather.TEMP_MAX - container.weather.TEMP_MIN

                # Strategy to estimate hourly air temperature.  agronomy@isci.it, February 2008. Campbell, G.S. 1985. Soil physics with BASIC: transport models for soil-plant systems.
                # HAT Campbell
                HourlyTemperatureMeristematicApex = []
                CampbellTimingVariation = 15
                for j in range(24):
                    HourlyTemperatureMeristematicApex.append(Tavg + DT / 2 * math.cos(0.2618 * (j - CampbellTimingVariation)))

                for j in range(24):
                    DailyStress = DailyStress + self.HourlySterilityFactor(HourlyTemperatureMeristematicApex[j], p.ThresholdTemperatureInducingSterilityBeforeFlowering)

                Delta = 0.125
                if (self.HighSensitivityForManyDays == True):
                    Delta = Delta * 1.5

                Sigma = Delta / 2.51
                DevelopmentStageCodeExactlyBetweenPanicleInitiationAndHeading = 1.75

                r.ColdInducedSpikeletSterilityRate = p.SensitivityToColdShockInducedSterility * DailyStress * self.BellFactor(s.DevelopmentStageCode, DevelopmentStageCodeExactlyBetweenPanicleInitiationAndHeading, Sigma, Delta) / 100;

            else:
                if s.DevelopmentStageCode > 1.9 and s.DevelopmentStageCode <= 2.1:

                    Tavg = (container.weather.TEMP_MAX + container.weather.TEMP_MIN) / 2
                    DT = container.weather.TEMP_MAX - container.weather.TEMP_MIN

                    # Strategy to estimate hourly air temperature.  agronomy@isci.it, February 2008. Campbell, G.S. 1985. Soil physics with BASIC: transport models for soil-plant systems.
                    # HAT Campbell
                    HourlyTemperatureMeristematicApex = []
                    CampbellTimingVariation = 15
                    for j in range(24):
                        HourlyTemperatureMeristematicApex.append(Tavg + DT / 2 * math.cos(0.2618 * (j - CampbellTimingVariation)))

                    for j in range(24):
                        DailyStress = DailyStress + self.HourlySterilityFactor(HourlyTemperatureMeristematicApex[j], p.ThresholdTemperatureInducingSterilityDuringFlowering)

                    Delta = 0.125 / 2.0
                    if (self.HighSensitivityForManyDays == True):
                        Delta = Delta * 1.5

                    Sigma = Delta / 2.51

                    DevelopmentStageCodeExactlyBetweenPanicleInitiationAndHeading = 2.0

                    r.ColdInducedSpikeletSterilityRate = p.SensitivityToColdShockInducedSterility * DailyStress * self.BellFactor(s.DevelopmentStageCode, DevelopmentStageCodeExactlyBetweenPanicleInitiationAndHeading, Sigma, Delta) / 100;

                else:

                    r.ColdInducedSpikeletSterilityRate = 0

            s.ColdInducedSpikeletSterilityState = s.ColdInducedSpikeletSterilityState + r.ColdInducedSpikeletSterilityRate
            if (s.ColdInducedSpikeletSterilityState > 1):
                s.ColdInducedSpikeletSterilityState = 1



        except  Exception as e:
            print('Error in method runstep of class ColdInducedSterilityWARM:' + str(e))


        return container

    def BellFactor(self, DVS, DVSmiddle, Sigma, Delta):

        if (DVS >= 1.6 and DVS <= 2.1):

            F1 = Delta / (Sigma * (math.pow((2 * math.pi), 0.5)))

            expo = -((math.pow((DVS - DVSmiddle), 2)) / (2 * (math.pow(Sigma, 2))))

            F2 = math.exp(expo)
            result = F1 * F2

        else:

            result = 0

        return result

    def HourlySterilityFactor(self, Thour, ThresholdT):

        if (Thour > ThresholdT):

            result = 0

        else:

            result = ThresholdT - Thour

        return result
