class LinkCo2DataToAssimilation:
    """ This step links the output of CO2Data step (Co2EffectOnAMAX,Co2EffectOnEFF) to the Wofost assimilation step"""

    def getparameterslist(self):
        return {}  # no parameters in this step

    def setparameters(self, status):
        return status

    def initialize(self, status):
        return status

    def runstep(self, status):
        status.assimilation.params.Co2EffectOnAMAX = status.co2data.Co2EffectOnAMAX
        status.assimilation.params.Co2EffectOnEFF = status.co2data.Co2EffectOnEFF
        return status

    def integrate(self, status):
        return status
