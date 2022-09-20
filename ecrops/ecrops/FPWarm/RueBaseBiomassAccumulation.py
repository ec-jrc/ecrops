
class RueBaseBiomassAccumulation():
    """
    RUE based biomass accumulation. Reference: Monteith, J.L. 1977. Climate and the efficiency of crop production in Britain.
    Philos. Trans. R. Soc. London, Ser. B. Biol. Sci. 281:277-294
    """
    def setparameters(self, container):
        return container

    def initialize(self, container):
        return container

    def integrate(self, container):
        return container

    def getparameterslist(self):
        return {
            "PARtoGlobalRadiationFactor": {"Description": "Photosynthetically active radiation to global radiation factor",
                                    "Type": "Number",
                                    "Mandatory": "True", "UnitOfMeasure": "MJ m-2 d-1"},
        }


    def runstep(self, container):

        try :
            ex = container.Weather[(container.day - container.first_day).days]  # get the meteo data for current day
            p = container.Parameters  # parameters
            s = container.States  # states
            s1 = container.States1  # ???
            a = container.Auxiliary  # ???
            r = container.Rates  # rates

            if (s.DevelopmentStageCode >= 0 and s.DevelopmentStageCode <= 3):

                r.BiomassRadiationDependentRate = r.RUEActualRate * p.PARtoGlobalRadiationFactor * \
                                                  r.AbsorbedSolarRadiationRate * 10
                # 10 transforms g m - 2 to kg  ha - 1

                r.AbovegroundBiomassRate = r.BiomassRadiationDependentRate

            else:
                r.BiomassRadiationDependentRate = 0
                r.AbovegroundBiomassRate = 0

            s1.BiomassRadiationDependent = s.BiomassRadiationDependent + r.BiomassRadiationDependentRate
            s1.AbovegroundBiomass = s.AbovegroundBiomass + r.AbovegroundBiomassRate

        except  Exception as e:
            print('Error in method runstep of class RueBaseBiomassAccumulation:'+str(e))

        return container