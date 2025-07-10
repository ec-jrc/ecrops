from ecrops.Step import Step


class PartitioningWarm(Step):
    """Aboveground biomass partitioning. Reference: Confalonieri, R., Gusberti, D., Acutis, M., 2006. Comparison of WOFOST, CropSyst and WARM for
    simulating rice growth (Japonica type – short cycle varieties). Italian Journal of Agrometeorology, 3, 7-16"""

    def setparameters(self, container):
        if not hasattr(container, 'WarmParameters'):
            from ecrops.Printable import Printable
            container.WarmParameters = Printable()
        container.WarmParameters.PartitioningToLeavesAtEmergence = container.allparameters['PartitioningToLeavesAtEmergence']

        return container

    def initialize(self, container):
        container.states.ColdInducedSpikeletSterilityState = 0
        container.states.HeatInducedSpikeletSterilityState = 0
        container.auxiliary.Sterility=0
        container.states.LeavesBiomass = 0
        container.states.StemsBiomass = 0
        container.states.StorageOrgansBiomass = 0
        return container

    def integrate(self, container):
        s = container.states  # states
        r = container.rates  # rates

        return container

    def getparameterslist(self):
        return {
            "PartitioningToLeavesAtEmergence": {"Description": "Partitioning to leaves at emergence", "Type": "Number",
                                                "Mandatory": "True", "UnitOfMeasure": "unitess"},
        }

    def getinputslist(self):
        return {

            "DevelopmentStageCode": {"Description": "Development stage", "Type": "Number", "UnitOfMeasure": "unitless",
                                     "StatusVariable": "status.states.DevelopmentStageCode"},
            "AbovegroundBiomassRate": {"Description": "Aboveground biomass rate",
                                  "Type": "Number",
                                  "UnitOfMeasure": "kg/ha",
                                  "StatusVariable": "status.rates.AbovegroundBiomassRate"},
            "ColdInducedSpikeletSterilityState": {"Description": "Cold induced spikelet sterility",
                                                  "Type": "Number",
                                                  "UnitOfMeasure": "unitless",
                                                  "StatusVariable": "status.states.ColdInducedSpikeletSterilityState"},
            "HeatInducedSpikeletSterilityState": {"Description": "Heat induced spikelet sterility",
                                                  "Type": "Number",
                                                  "UnitOfMeasure": "unitless",
                                                  "StatusVariable": "status.states.HeatInducedSpikeletSterilityState"},
            "StorageOrgansBiomass": {"Description": "Storage organs biomass ",
                                     "Type": "Number",
                                     "UnitOfMeasure": "kg/ha",
                                     "StatusVariable": "status.states.StorageOrgansBiomass"},
            "StemsBiomass": {"Description": "Stems biomass ",
                             "Type": "Number",
                             "UnitOfMeasure": "kg/ha",
                             "StatusVariable": "status.states.StemsBiomass"},
            "LeavesBiomass": {"Description": "Leaves biomass ",
                              "Type": "Number",
                              "UnitOfMeasure": "kg/ha",
                              "StatusVariable": "status.states.LeavesBiomass"},
            "Sterility": {"Description": "Sterility (cold plus heat induced sterility)",
                          "Type": "Number",
                          "UnitOfMeasure": "unitless",
                          "StatusVariable": "status.auxiliary.Sterility"},
        }

    def getoutputslist(self):
        return {
            "LeavesBiomassRate": {"Description": "Leaves biomass rate",
                              "Type": "Number",
                              "UnitOfMeasure": "kg/ha",
                              "StatusVariable": "status.rates.LeavesBiomassRate"},
            "StorageOrgansBiomassRate": {"Description": "Storage organs biomass rate",
                                  "Type": "Number",
                                  "UnitOfMeasure": "kg/ha",
                                  "StatusVariable": "status.rates.StorageOrgansBiomassRate"},
            "StemsBiomassRate": {"Description": "Stems biomass rate",
                                         "Type": "Number",
                                         "UnitOfMeasure": "kg/ha",
                                         "StatusVariable": "status.rates.StemsBiomassRate"},
            "LeavesBiomass": {"Description": "Leaves biomass ",
                                  "Type": "Number",
                                  "UnitOfMeasure": "kg/ha",
                                  "StatusVariable": "status.states.LeavesBiomass"},
            "StorageOrgansBiomass": {"Description": "Storage organs biomass ",
                                         "Type": "Number",
                                         "UnitOfMeasure": "kg/ha",
                                         "StatusVariable": "status.states.StorageOrgansBiomass"},
            "StemsBiomass": {"Description": "Stems biomass ",
                                 "Type": "Number",
                                 "UnitOfMeasure": "kg/ha",
                                 "StatusVariable": "status.states.StemsBiomass"},
            "Sterility": {"Description": "Sterility (cold plus heat induced sterility)",
                                  "Type": "Number",
                                  "UnitOfMeasure": "unitless",
                                  "StatusVariable": "status.auxiliary.Sterility"},

        }

    def runstep(self, container):

        try:

            p = container.WarmParameters  # parameters
            s = container.states  # states
            r = container.rates  # rates
            a = container.auxiliary

            r.LeavesBiomassRate = r.AbovegroundBiomassRate * self.PartitioningToLeaves(
                p.PartitioningToLeavesAtEmergence,
                s.DevelopmentStageCode)

            #put togheter cold and heat sterility  (1= max sterility, 0= no sterility)
            a.Sterility = min(1, s.ColdInducedSpikeletSterilityState + s.HeatInducedSpikeletSterilityState)

            r.StorageOrgansBiomassRate = r.AbovegroundBiomassRate * self.PartitioningToStorageOrgans(
                s.DevelopmentStageCode) * (1 - a.Sterility)

            r.StemsBiomassRate = r.AbovegroundBiomassRate - r.LeavesBiomassRate - r.StorageOrgansBiomassRate

            s.LeavesBiomass = s.LeavesBiomass + r.LeavesBiomassRate
            s.StemsBiomass = s.StemsBiomass + r.StemsBiomassRate
            s.StorageOrgansBiomass = s.StorageOrgansBiomass + r.StorageOrgansBiomassRate

        except  Exception as e:
            print('Error in method runstep of class PartitionWarm:' + str(e))

        return container


    def PartitioningToLeaves(self, RipL0, DVS):
        """
        Rate of biomass allocated to the leaves
        """
        if (DVS >= 1 and DVS <= 2):
            result = -RipL0 * (DVS ** 2) + 2 * DVS * RipL0

        else:
            result = 0

        if (result < 0):
            result = 0

        if (result > 1):
            result = 1

        return result


    def PartitioningToStorageOrgans(self, DVS):
        """
        Rate of biomass allocated to the storage organs
        """
        if DVS < 1.6:
            result = 0

        else:
            if (DVS > 2.5):
                result = 1

            else:
                result = -1.8751 * ((DVS ** 2)) + 9.1817 * DVS - 10.2121

        if (result < 0):
            result = 0

        if (result > 1):
            result = 1

        return result
