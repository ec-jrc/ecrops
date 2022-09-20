class LinkCo2DataToEvapotranspiration:
    """ This step links the output of CO2Data step (Co2EffectOnPotentialTraspiration) to the Wofost evapotranspiration step"""

    def getparameterslist(self):
        return {}  # no parameters in this step

    def setparameters(self, status):
        return status

    def initialize(self, status):
        return status

    def runstep(self, status):
        status.evapotranspiration.params.Co2EffectOnPotentialTraspiration = status.co2data.Co2EffectOnPotentialTraspiration

        return status

    def integrate(self, status):
        return status
