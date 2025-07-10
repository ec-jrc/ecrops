from ecrops.Step import Step


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
class PotentialPhenology(Step):
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
        if not hasattr(container, 'WarmParameters'):
            from ecrops.Printable import Printable
            container.WarmParameters = Printable()
        container.WarmParameters.GrowingDegreeDaysToReachEmergence = container.allparameters['GrowingDegreeDaysToReachEmergence']
        container.WarmParameters.GrowingDegreeDaysToReachFlowering = container.allparameters['GrowingDegreeDaysToReachFlowering']
        container.WarmParameters.GrowingDegreeDaysToReachMaturity = container.allparameters['GrowingDegreeDaysToReachMaturity']
        container.WarmParameters.GrowingDegreeDaysToReachHarvest = container.allparameters['GrowingDegreeDaysToReachHarvest']
        return container

    def initialize(self, container):
        container.states.DevelopmentStageCode = 0
        container.states.GrowingDegreeDays = 0
        container.states.DOS = None
        container.rates.GrowingDegreeDaysRate = 0
        container.auxiliary.VernalizationFactor = 1
        container.auxiliary.PhotoPeriodFactor = 1
        return container

    def integrate(self, container):
        s = container.states  # states
        p = container.WarmParameters  # parameters
        a = container.auxiliary
        r = container.rates  # rates

        s.DevelopmentStageCode = 0
        # sowing - emergence
        if s.GrowingDegreeDays < p.GrowingDegreeDaysToReachEmergence:
            s.DevelopmentStageCode = s.GrowingDegreeDays / p.GrowingDegreeDaysToReachEmergence

        # emergence - flowering
        else:
            if s.GrowingDegreeDays >= p.GrowingDegreeDaysToReachEmergence and s.GrowingDegreeDays < \
                    (p.GrowingDegreeDaysToReachFlowering + p.GrowingDegreeDaysToReachEmergence):
                s.DevelopmentStageCode = 1 + ((s.GrowingDegreeDays - p.GrowingDegreeDaysToReachEmergence) /
                                              (p.GrowingDegreeDaysToReachFlowering))

            # flowering - maturity
            else:
                if s.GrowingDegreeDays >= (p.GrowingDegreeDaysToReachEmergence +
                                               p.GrowingDegreeDaysToReachFlowering) and \
                                s.GrowingDegreeDays < (p.GrowingDegreeDaysToReachEmergence +
                                                           p.GrowingDegreeDaysToReachFlowering +
                                                           p.GrowingDegreeDaysToReachMaturity):
                    s.DevelopmentStageCode = 2 + ((
                                                      s.GrowingDegreeDays - p.GrowingDegreeDaysToReachEmergence - p.GrowingDegreeDaysToReachFlowering) / p.GrowingDegreeDaysToReachMaturity)

                # maturity - harvest
                else:
                    if s.GrowingDegreeDays >= (
                                    p.GrowingDegreeDaysToReachEmergence + p.GrowingDegreeDaysToReachFlowering + p.GrowingDegreeDaysToReachMaturity):
                        s.DevelopmentStageCode = 3 + ((
                                                          s.GrowingDegreeDays - p.GrowingDegreeDaysToReachEmergence - p.GrowingDegreeDaysToReachFlowering - p.GrowingDegreeDaysToReachMaturity) / p.GrowingDegreeDaysToReachHarvest);

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
            "GrowingDegreeDaysToReachHarvest": {"Description": "Growing degree days to reach harvest",
                                                "Type": "Number",
                                                "Mandatory": "True", "UnitOfMeasure": "C"},

        }

    def runstep(self, container):

        try:

            p = container.WarmParameters  # parameters
            s = container.states  # states

            a = container.auxiliary
            r = container.rates  # rates

            # at sowing
            if container.day == container.sowing_emergence_day:
                s.DOS = container.day
            # before sowing and emergence
            if container.states.DOS is None:
                return container

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

            s.GrowingDegreeDays = s.GrowingDegreeDays + r.GrowingDegreeDaysRate



        except  Exception as e:
            print('Error in method runstep of class PotentialPhenology:' + str(e))

        return container

    def getinputslist(self):
        return {
            "day": {"Description": "Current day", "Type": "Number", "UnitOfMeasure": "doy",
                    "StatusVariable": "status.day"},
            "sowing_emergence_day": {"Description": "Doy of sowing or emergence", "Type": "Number",
                                     "UnitOfMeasure": "doy",
                                     "StatusVariable": "status.sowing_emergence_day"},
            "DevelopmentStageCode": {"Description": "Development stage", "Type": "Number", "UnitOfMeasure": "unitless",
                                     "StatusVariable": "status.states.DevelopmentStageCode"},
            "GrowingDegreeDays": {"Description": "Growing degree days",
                                  "Type": "Number",
                                  "UnitOfMeasure": "C",
                                  "StatusVariable": "status.states.GrowingDegreeDays"},
            "GrowingDegreeDaysTemperatureRate": {"Description": "Growing degree days by temperature rate",
                                                 "Type": "Number",
                                                 "UnitOfMeasure": "C",
                                                 "StatusVariable": "status.rates.GrowingDegreeDaysTemperatureRate"},

            "UsePhotoPeriod": {"Description": "Booelan to use the photo period effect on phenology", "Type": "Boolean",
                               "UnitOfMeasure": "unitless",
                               "StatusVariable": "status.UsePhotoPeriod"},
            "UseVernalization": {"Description": "Booelan to use the vernalization", "Type": "Boolean",
                                 "UnitOfMeasure": "unitless",
                                 "StatusVariable": "status.UseVernalization"},
            "VernalizationFactor": {"Description": "Vernalization factor on phenology", "Type": "Number",
                                    "UnitOfMeasure": "unitless",
                                    "StatusVariable": "status.auxiliary.VernalizationFactor"},
            "PhotoPeriodFactor": {"Description": "Photo period factor on phenology", "Type": "Number",
                                  "UnitOfMeasure": "unitless",
                                  "StatusVariable": "status.auxiliary.PhotoPeriodFactor"},

        }

    def getoutputslist(self):
        return {
            "DOS": {"Description": "Doy of sowing", "Type": "Number", "UnitOfMeasure": "doy",
                    "StatusVariable": "status.states.DOS"},

            "GrowingDegreeDaysRate": {"Description": "Growing degree days rate",
                                      "Type": "Number",
                                      "UnitOfMeasure": "C",
                                      "StatusVariable": "status.rates.GrowingDegreeDaysRate"},
            "GrowingDegreeDays": {"Description": "Growing degree days",
                                  "Type": "Number",
                                  "UnitOfMeasure": "C",
                                  "StatusVariable": "status.states.GrowingDegreeDays"},
        }
