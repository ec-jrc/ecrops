

class EnableCo2Effect:
    """When this step is inserted in a workflow after the 'DisableCo2Effect' step, it re-enables the CO2 effects on plant."""

    def getparameterslist(self):
        return {}  # no parameters in this step

    def setparameters(self, status):
        return status

    def initialize(self, status):
        return status

    def runstep(self, status):
        status.co2data.Co2EffectOnAMAX = status.co2data.TempCo2EffectOnAMAX
        status.co2data.Co2EffectOnEFF = status.co2data.TempCo2EffectOnEFF
        status.co2data.Co2EffectOnPotentialTraspiration = status.co2data.TempCo2EffectOnPotentialTraspiration
        status.co2data.DMI_NoCo2 = status.rates.DMI
        return status

    def integrate(self, status):
        return status
