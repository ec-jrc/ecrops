from ..Printable import Printable


class HeatStress:
    """Calculation of the Heat Stress"""

    def getparameterslist(self):
        return {
            "NUMBER_OF_DAYS_AROUND_FLOWERING": {
                "Description": "Number of days to consider before and after flowering as flowering period",
                "Type": "Number", "Mandatory": "True",
                "UnitOfMeasure": "days"},
            "TDamage": {"Description": "Damage base temperature", "Type": "Number", "Mandatory": "True",
                        "UnitOfMeasure": "C"},
            "TKill": {"Description": "Kill threshold temperature", "Type": "Number", "Mandatory": "True",
                      "UnitOfMeasure": "unitless"},
            "AnthesysPeriodDamegeComputationMethod": {
                "Description": "How to compute anthesys period damage (could be:Average of the damages,Greater of the damages,Product of the damages)",
                "Type": "String", "Mandatory": "True",
                "UnitOfMeasure": "unitless"},
            "ReductionFactorMethod": {"Description": "Reduction factor function (could be: Quadratic,Linear)",
                                      "Type": "String", "Mandatory": "True",
                                      "UnitOfMeasure": "unitless"}
        }

    def setparameters(self, status):
        status.heatstress = Printable()
        status.heatstress.params = Printable()
        status.heatstress.params.NUMBER_OF_DAYS_AROUND_FLOWERING = status.NUMBER_OF_DAYS_AROUND_FLOWERING
        status.heatstress.params.TDamage = status.TDamage
        status.heatstress.params.TKill = status.TKill
        status.heatstress.params.AnthesysPeriodDamegeComputationMethod = status.AnthesysPeriodDamegeComputationMethod
        status.heatstress.params.ReductionFactorMethod = status.ReductionFactorMethod
        return status

    def initialize(self, status):
        status.heatstress.canopytemperature = 0
        status.heatstress.DailyHeatStressFactor = 1
        status.heatstress.CanopyTemperatureLastNdays = []
        status.heatstress.DailyStressesAroundAnthesis = []
        status.heatstress.CanopyTemperatureSinceNDaysAfterAnthesis = []
        status.heatstress.HIMAX = 1  # maximum attainable heat stress (always 1 by convention)
        status.heatstress.AnthesisReached = False
        status.heatstress.MaturityReached = False
        status.heatstress.DaysAfterAnthesis = -1;
        status.heatstress.FinalHarvestIndex = status.heatstress.HIMAX
        status.heatstress.TemporaryHarvestIndex = status.heatstress.HIMAX
        status.heatstress.HarvestIndexAfterAnthesis = status.heatstress.HIMAX

        return status

    def CalculateLinearReductionFactor(self, canopyTemperature, tdamage, tkill):

        if (canopyTemperature <= tdamage):
            return 1
        if (canopyTemperature >= tkill):
            return 0

        if (tdamage < canopyTemperature and canopyTemperature < tkill):
            return (1 / (tdamage - tkill)) * canopyTemperature - (tkill / (tdamage - tkill))

        raise Exception(
            "Inconsistent status: canopytemp=" + canopyTemperature + " tdamage=" + tdamage + " tkill= " + tkill)  # should never happen

    def CalculateQuadraticReductionFactor(self, canopyTemperature, tdamage, tkill):

        if (canopyTemperature <= tdamage):
            return 1
        if (canopyTemperature >= tkill):
            return 0

        if (tdamage < canopyTemperature and canopyTemperature < tkill):
            return 1 - (((canopyTemperature - tdamage) / (tkill - tdamage)) ** 2)

        raise Exception(
            "Inconsistent status: canopytemp=" + canopyTemperature + " tdamage=" + tdamage + " tkill= " + tkill)  # should never happen

    def runstep(self, status):

        status.heatstress.DailyHeatStressFactor = 1;  # no stress by default
        p = status.heatstress.params

        if (status.states.DVS == 0):  # when there is no crop
            # clear all the lists
            status.heatstress.DailyStressesAroundAnthesis = []
            status.heatstress.CanopyTemperatureSinceNDaysAfterAnthesis = []
            status.heatstress.CanopyTemperatureLastNdays = []

        # before anthesis store the canopy temp of previous NUMBER_OF_DAYS_AROUND_FLOWERING days
        if (status.states.DVS < 1):
            # add canopy temperature  of current day
            status.heatstress.CanopyTemperatureLastNdays.append(status.heatstress.canopytemperature)

            # if the lenght of the list is greater than the  NUMBER_OF_DAYS_AROUND_FLOWERING parameter
            if (len(status.heatstress.CanopyTemperatureLastNdays) > (p.NUMBER_OF_DAYS_AROUND_FLOWERING + 1)):
                del status.heatstress.CanopyTemperatureLastNdays[0]  # remove the oldest value

        if (status.states.DVS < 1):  # before anthesis initialize the ouputs
            status.heatstress.AnthesisReached = False
            status.heatstress.MaturityReached = False
            status.heatstress.DaysAfterAnthesis = -1;
            status.heatstress.FinalHarvestIndex = status.heatstress.HIMAX
            status.heatstress.TemporaryHarvestIndex = status.heatstress.HIMAX
            status.heatstress.HarvestIndexAfterAnthesis = status.heatstress.HIMAX

        # after anthesis, but before maturity
        if (status.states.DVS >= 1 and status.states.DVS < 2 and status.plantheight.PlantHeight > 0):
            status.heatstress.MaturityReached = False;
            status.heatstress.AnthesisReached = True;
            status.heatstress.DaysAfterAnthesis = status.heatstress.DaysAfterAnthesis + 1;

            if (status.heatstress.DaysAfterAnthesis == 0):  # the anthesis day (do the calculation on current day and also on previous NUMBER_OF_DAYS_AROUND_FLOWERING days)

                for canopyTemperatureLast7Day in status.heatstress.CanopyTemperatureLastNdays:  # at this day, the list contains NUMBER_OF_DAYS_AROUND_FLOWERING elements, all NUMBER_OF_DAYS_AROUND_FLOWERING the days before anthesys

                    linearHeatStressFactor2 = self.CalculateLinearReductionFactor(canopyTemperatureLast7Day, p.TDamage,
                                                                                  p.TKill)
                    quadraticHeatStessFactor2 = self.CalculateQuadraticReductionFactor(canopyTemperatureLast7Day,
                                                                                       p.TDamage, p.TKill)
                    if (p.ReductionFactorMethod == "Linear"):
                        status.heatstress.DailyHeatStressFactor = linearHeatStressFactor2
                    else:
                        status.heatstress.DailyHeatStressFactor = quadraticHeatStessFactor2

                    if (status.heatstress.DailyHeatStressFactor < 1):
                        status.heatstress.DailyStressesAroundAnthesis.append(
                            status.heatstress.DailyHeatStressFactor)  # save the stress factor ( if different from 1) to the list of stress factors around anthesys

        # the NUMBER_OF_DAYS_AROUND_FLOWERING days after the anthesis day (do the calculation on current day)
        if (
                status.heatstress.DaysAfterAnthesis > 0 and status.heatstress.DaysAfterAnthesis <= p.NUMBER_OF_DAYS_AROUND_FLOWERING):

            linearHeatStressFactor2 = self.CalculateLinearReductionFactor(status.heatstress.canopytemperature,
                                                                          p.TDamage, p.TKill)
            quadraticHeatStessFactor2 = self.CalculateQuadraticReductionFactor(status.heatstress.canopytemperature,
                                                                               p.TDamage, p.TKill)
            if (p.ReductionFactorMethod == "Linear"):
                status.heatstress.DailyHeatStressFactor = linearHeatStressFactor2
            else:
                status.heatstress.DailyHeatStressFactor = quadraticHeatStessFactor2

            if (status.heatstress.DailyHeatStressFactor < 1):
                status.heatstress.DailyStressesAroundAnthesis.append(
                    status.heatstress.DailyHeatStressFactor)  # save the stress factor ( if different from 1) to the list of stress factors around anthesys

            if (
                status.heatstress.DaysAfterAnthesis == p.NUMBER_OF_DAYS_AROUND_FLOWERING):  # the last day of the anthesis period (from this day HarvestIndexAfterAnthesis does not change anymore)

                cumulativeStressFactorAroundAnthesys = 1;

                if (
                    p.AnthesysPeriodDamegeComputationMethod == "Average of the damages"):  # the final stress factor during anthesys is the average of the stress factors happened during the anthesys period.If no stress happened, then is 1

                    if (len(status.heatstress.DailyStressesAroundAnthesis) > 0):
                        cumulativeStressFactorAroundAnthesys = sum(status.heatstress.DailyStressesAroundAnthesis) / len(
                            status.heatstress.DailyStressesAroundAnthesis)


                else:
                    if (
                        p.AnthesysPeriodDamegeComputationMethod == "Greater of the damages"):  # the final stress factor during anthesys is the greater of the stress factors happened during the anthesys period.If no stress happened, then is 1

                        if (len(status.heatstress.DailyStressesAroundAnthesis) > 0):
                            cumulativeStressFactorAroundAnthesys = max(status.heatstress.DailyStressesAroundAnthesis)

                    else:
                        if (
                            p.AnthesysPeriodDamegeComputationMethod == "Product of the damages"):  # the final stress factor during anthesys is the product of the stress factors happened during the anthesys period.If no stress happened, then is 1

                            if (len(status.heatstress.DailyStressesAroundAnthesis) > 0):
                                for v in status.heatstress.DailyStressesAroundAnthesis:
                                    cumulativeStressFactorAroundAnthesys = v * cumulativeStressFactorAroundAnthesys

                status.heatstress.HarvestIndexAfterAnthesis = cumulativeStressFactorAroundAnthesys * status.heatstress.HarvestIndexAfterAnthesis
                status.heatstress.FinalHarvestIndex = status.heatstress.HarvestIndexAfterAnthesis

        if (status.states.DVS >= 2):  # after maturity
            status.heatstress.MaturityReached = True
            status.heatstress.DailyHeatStressFactor = 1  # no stress by default after maturity

        # HERE we skip completely the calculation of the harvest index after the NUMBER_OF_DAYS_AROUND_FLOWERING days after the anthesis day to maturity, and after maturity.
        # We calculate the impact of heat stress in this period directly in the WOFOST mdoel, as impact on the biomasses of Wofost.
        # In the Bioma version there is an alternative way for calculating the heat stress also in this period, but we dont implement it here


        return status

    def integrate(self, status):
        return status

