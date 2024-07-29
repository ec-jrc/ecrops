from ecrops.Step import Step

class CO2EffectOnRue(Step):
    """
    CO2 Effect on Rue. Reference: Stockle, C.O., Donatelli, M., Nelson, R., 2003. CropSyst, a cropping systems simulation model.
    # European Journal of Agronomy, 18, 289-307
    """

    def setparameters(self, container):
        container.WarmParameters.IsC3 = container.allparameters['IsC3']

        return container

    def initialize(self, container):
        return container

    def integrate(self, container):
        return container

    def getparameterslist(self):
        return {
            "IsC3": {"Description": "1 if crop is a C3 crop, any other number if crop is a C4 crop", "Type": "Number",
                     "Mandatory": "True", "UnitOfMeasure": "unitess"},
        }

    def getinputslist(self):
        return {

            "Co2Concentration": {"Description": "Co2 Concentration", "Type": "Number",
                       "UnitOfMeasure": "ppm",
                       "StatusVariable": "status.Co2Concentration"},


        }

    def getoutputslist(self):
        return {
            "GrowthRatioCO2": {"Description": "Growth on RUE due to CO2 concentration", "Type": "Number",
                               "UnitOfMeasure": "unitless",
                               "StatusVariable": "status.auxiliary.GrowthRatioCO2"},

        }

    def runstep(self, container):

        try:
            p = container.WarmParameters  # parameters
            a = container.auxiliary

            if p.IsC3 == 1:
                a.GrowthRatioCO2 = 0.0007 * container.Co2Concentration + 0.75

            else:
                a.GrowthRatioCO2 = 0.0003 * container.Co2Concentration + 0.9

        except Exception as e:
            print('Error in method runstep of class CO2EffectOnRue:' + str(e))

        return container
