from ecrops.Step import Step
class RueBaseBiomassAccumulation(Step):
    """
    RUE based biomass accumulation. Reference: Monteith, J.L. 1977. Climate and the efficiency of crop production in Britain.
    Philos. Trans. R. Soc. London, Ser. B. Biol. Sci. 281:277-294
    """
    def setparameters(self, container):
        container.WarmParameters.PARtoGlobalRadiationFactor = container.allparameters['PARtoGlobalRadiationFactor']

        return container

    def initialize(self, container):
        container.states.BiomassRadiationDependent = 0
        container.states.AbovegroundBiomass = 0
        return container

    def integrate(self, container):
        s = container.states  # states
        r = container.rates  # rates


        return container

    def getparameterslist(self):
        return {
            "PARtoGlobalRadiationFactor": {"Description": "Photosynthetically active radiation to global radiation factor",
                                    "Type": "Number",
                                    "Mandatory": "True", "UnitOfMeasure": "MJ m-2 d-1"},
        }


    def runstep(self, container):

        try :

            p = container.WarmParameters  # parameters
            s = container.states  # states
            r = container.rates  # rates

            if (s.DevelopmentStageCode >= 0 and s.DevelopmentStageCode <= 3):

                r.BiomassRadiationDependentRate = r.RUEActualRate * p.PARtoGlobalRadiationFactor * \
                                                  r.AbsorbedSolarRadiationRate * 10
                # 10 transforms g m - 2 to kg  ha - 1

                r.AbovegroundBiomassRate = r.BiomassRadiationDependentRate

            else:
                r.BiomassRadiationDependentRate = 0
                r.AbovegroundBiomassRate = 0

            s.BiomassRadiationDependent = s.BiomassRadiationDependent + r.BiomassRadiationDependentRate
            s.AbovegroundBiomass = s.AbovegroundBiomass + r.AbovegroundBiomassRate

        except  Exception as e:
            print('Error in method runstep of class RueBaseBiomassAccumulation:'+str(e))

        return container

    def getinputslist(self):
        return {

            "DevelopmentStageCode": {"Description": "Development stage", "Type": "Number", "UnitOfMeasure": "unitless",
                                     "StatusVariable": "status.states.DevelopmentStageCode"},
            "RUEActualRate": {"Description": "RUE Actual Rate", "Type": "Number",
                              "UnitOfMeasure": "",
                              "StatusVariable": "status.rates.RUEActualRate"},
            "AbsorbedSolarRadiationRate": {"Description": "Absorbed solar radiation rate",
                                           "Type": "Number",
                                           "UnitOfMeasure": "unitless",
                                           "StatusVariable": "status.rates.AbsorbedSolarRadiationRate"},
            "AbovegroundBiomass": {"Description": "Aboveground biomass",
                                   "Type": "Number",
                                   "UnitOfMeasure": "kg/ha",
                                   "StatusVariable": "status.states.AbovegroundBiomass"},
            "BiomassRadiationDependent": {"Description": "Biomass radiation dependent",
                                          "Type": "Number",
                                          "UnitOfMeasure": "kg/ha",
                                          "StatusVariable": "status.states.BiomassRadiationDependent"},
        }

    def getoutputslist(self):
        return {

            "AbovegroundBiomassRate": {"Description": "Aboveground biomass rate",
                                       "Type": "Number",
                                       "UnitOfMeasure": "kg/ha",
                                       "StatusVariable": "status.rates.AbovegroundBiomassRate"},
            "BiomassRadiationDependentRate": {"Description": "Biomass radiation dependent rate",
                                       "Type": "Number",
                                       "UnitOfMeasure": "kg/ha",
                                       "StatusVariable": "status.rates.BiomassRadiationDependentRate"},
            "AbovegroundBiomass": {"Description": "Aboveground biomass",
                                       "Type": "Number",
                                       "UnitOfMeasure": "kg/ha",
                                       "StatusVariable": "status.states.AbovegroundBiomass"},
            "BiomassRadiationDependent": {"Description": "Biomass radiation dependent",
                                              "Type": "Number",
                                              "UnitOfMeasure": "kg/ha",
                                              "StatusVariable": "status.states.BiomassRadiationDependent"},
        }