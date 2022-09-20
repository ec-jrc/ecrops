import copy


# -----------------------------------------------
# Phenology step
# Listed below are decimal codes for the main stages:
#
# Sowing: 0.00
# Emergence: 1.00
# Beginning of tillering: 1.25
# Mid tillering: 1.35
# Panicle initiation: 1.60
# Full Heading: 1.90
# Full Flowering: 2.00
# Full Grain filling: 2.50
# Physiological maturity: 3.00
# Harvestable: 4.00
# -----------------------------------------------
class PotentialPhenology():
    """
    WARM Phenology.
    Listed below are decimal codes for the main stages:

    # Sowing: 0.00
    # Emergence: 1.00
    # Beginning of tillering: 1.25
    # Mid tillering: 1.35
    # Panicle initiation: 1.60
    # Full Heading: 1.90
    # Full Flowering: 2.00
    # Full Grain filling: 2.50
    # Physiological maturity: 3.00
    # Harvestable: 4.00
    """

    def setparameters(self, container):
        return container

    def initialize(self, container):
        return container

    def integrate(self, container):
        return container

    def getparameterslist(self):
        return {
            "GrowingDegreeDaysToReachEmergence": {"Description": "Growing degree days to reach emergence",
                                                  "Type": "Number",
                                                  "Mandatory": "True", "UnitOfMeasure": "C"},
            "GrowingDegreeDaysToReachFlowering": {"Description": "Growing degree days to reach flowering",
                                                  "Type": "Number",
                                                  "Mandatory": "True", "UnitOfMeasure": "C"},
            "GrowingDegreeDaysToReachMaturity": {"Description": "Growing degree days to reach maturity",
                                                 "Type": "Number",
                                                 "Mandatory": "True", "UnitOfMeasure": "C"},
        }

    def runstep(self, container):

        try:
            ex = container.Weather[(container.day - container.first_day).days]  # get the meteo data for current day
            p = container.Parameters  # parameters
            s = container.States  # states
            s1 = container.States1  # ???
            a = container.Auxiliary  # ???
            r = container.Rates  # rates

            if s.DevelopmentStageCode >= 0 and s.DevelopmentStageCode < 1:  # sowing - emergence
                r.GrowingDegreeDaysRate = r.GrowingDegreeDaysTemperatureRate

            if s.DevelopmentStageCode >= 1 and s.DevelopmentStageCode < 2:  # emergence - flowering
                if container.UsePhotoPeriod == False and container.UseVernalization == False:  # no  photoperiod;  no vernalization
                    r.GrowingDegreeDaysRate = r.GrowingDegreeDaysTemperatureRate

                else:
                    if container.UsePhotoPeriod == False and container.UseVernalization == True:  # no photoperiod; yes vernalization
                        r.GrowingDegreeDaysRate = r.GrowingDegreeDaysTemperatureRate * a.VernalizationFactor

                    else:
                        if container.UsePhotoPeriod == True and container.UseVernalization == False:  # yes photoperiod; no vernalization
                            r.GrowingDegreeDaysRate = r.GrowingDegreeDaysTemperatureRate * a.PhotoPeriodFactor

                        else:  # yes photoperiod; yes vernalization
                            r.GrowingDegreeDaysRate = r.GrowingDegreeDaysTemperatureRate * a.PhotoPeriodFactor * a.VernalizationFactor

            if s.DevelopmentStageCode >= 2 and s.DevelopmentStageCode < 3:  # flowering - maturity
                r.GrowingDegreeDaysRate = r.GrowingDegreeDaysTemperatureRate

            if s.DevelopmentStageCode >= 3 and s.DevelopmentStageCode < 4:  # maturity - harvest
                r.GrowingDegreeDaysRate = r.GrowingDegreeDaysTemperatureRate

            if s.DevelopmentStageCode >= 4:
                r.GrowingDegreeDaysRate = 0

            s1.GrowingDegreeDays = s.GrowingDegreeDays + r.GrowingDegreeDaysRate

            DevelopmentStageDecimalCode = 0
            # sowing - emergence
            if s1.GrowingDegreeDays < p.GrowingDegreeDaysToReachEmergence:
                DevelopmentStageDecimalCode = s1.GrowingDegreeDays / p.GrowingDegreeDaysToReachEmergence

            # emergence - flowering
            else:
                if s1.GrowingDegreeDays >= p.GrowingDegreeDaysToReachEmergence and s1.GrowingDegreeDays < \
                        (p.GrowingDegreeDaysToReachFlowering + p.GrowingDegreeDaysToReachEmergence):
                    DevelopmentStageDecimalCode = 1 + ((s1.GrowingDegreeDays - p.GrowingDegreeDaysToReachEmergence) /
                                                       (p.GrowingDegreeDaysToReachFlowering))

                # flowering - maturity
                else:
                    if s1.GrowingDegreeDays >= (p.GrowingDegreeDaysToReachEmergence +
                                                p.GrowingDegreeDaysToReachFlowering) and \
                            s1.GrowingDegreeDays < (p.GrowingDegreeDaysToReachEmergence +
                                                    p.GrowingDegreeDaysToReachFlowering +
                                                    p.GrowingDegreeDaysToReachMaturity):
                        DevelopmentStageDecimalCode = 2 + ((
                                                                       s1.GrowingDegreeDays - p.GrowingDegreeDaysToReachEmergence - p.GrowingDegreeDaysToReachFlowering) / p.GrowingDegreeDaysToReachMaturity)

                    # maturity - harvest
                    else:
                        if s1.GrowingDegreeDays >= (
                                p.GrowingDegreeDaysToReachEmergence + p.GrowingDegreeDaysToReachFlowering + p.GrowingDegreeDaysToReachMaturity):
                            DevelopmentStageDecimalCode = 3 + ((
                                                                           s1.GrowingDegreeDays - p.GrowingDegreeDaysToReachEmergence - p.GrowingDegreeDaysToReachFlowering - p.GrowingDegreeDaysToReachMaturity) / p.GrowingDegreeDaysToReachHarvest);

            s1.DevelopmentStageCode = DevelopmentStageDecimalCode

        except  Exception as e:
            print('Error in method runstep of class PotentialPhenology:' + str(e))

        return container
