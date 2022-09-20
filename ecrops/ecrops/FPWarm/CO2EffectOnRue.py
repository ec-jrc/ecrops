class CO2EffectOnRue():
    """
    CO2 Effect on Rue. Reference: Stockle, C.O., Donatelli, M., Nelson, R., 2003. CropSyst, a cropping systems simulation model.
    # European Journal of Agronomy, 18, 289-307
    """

    def setparameters(self, container):
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

    def runstep(self, container):

        try:
            p = container.Parameters  # parameters
            a = container.Auxiliary  # ???

            if p.IsC3 == 1:
                a.GrowthRatioCO2 = 0.0007 * container.Co2Concentration + 0.75

            else:
                a.GrowthRatioCO2 = 0.0003 * container.Co2Concentration + 0.9

        except Exception as e:
            print('Error in method runstep of class CO2EffectOnRue:' + str(e))

        return container
