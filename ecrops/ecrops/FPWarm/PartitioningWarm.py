import copy


class PartitioningWarm():
    """Aboveground biomass partitioning. Reference: Confalonieri, R., Gusberti, D., Acutis, M., 2006. Comparison of WOFOST, CropSyst and WARM for
    simulating rice growth (Japonica type – short cycle varieties). Italian Journal of Agrometeorology, 3, 7-16"""

    def setparameters(self, container):
        return container

    def initialize(self, container):
        return container

    def integrate(self, container):
        return container

    def getparameterslist(self):
        return {
            "PartitioningToLeavesAtEmergence": {"Description": "Partitioning to leaves at emergence", "Type": "Number",
                                                "Mandatory": "True", "UnitOfMeasure": "unitess"},
        }

    def runstep(self, container):

        try:
            ex = container.Weather[(container.day - container.first_day).days]  # get the meteo data for current day
            p = container.Parameters  # parameters
            s = container.States  # states
            s1 = container.States1  # ???
            a = container.Auxiliary  # ???
            r = container.Rates  # rates

            r.LeavesBiomassRate = r.AbovegroundBiomassRate * self.PartitioningToLeaves(
                p.PartitioningToLeavesAtEmergence,
                s.DevelopmentStageCode)

            r.StorageOrgansBiomassRate = r.AbovegroundBiomassRate * self.PartitioningToStorageOrgans(
                s.DevelopmentStageCode) * (1 - a.Sterility)

            r.StemsBiomassRate = r.AbovegroundBiomassRate - r.LeavesBiomassRate - r.StorageOrgansBiomassRate

            s1.LeavesBiomass = s.LeavesBiomass + r.LeavesBiomassRate
            s1.StemsBiomass = s.StemsBiomass + r.StemsBiomassRate
            s1.StorageOrgansBiomass = s.StorageOrgansBiomass + r.StorageOrgansBiomassRate

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
