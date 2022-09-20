class LinkCanopyTemperatureToHeatStress():
    """Link class to move canopy temperature outputs to heat stress"""

    def getparameterslist(self):
        return {}  # no parameters in this step

    def setparameters(self, status):
        return status

    def initialize(self, status):
        return status

    def runstep(self, status):
        status.heatstress.canopytemperature = status.canopytemperature.canopytemperature
        return status

    def integrate(self, status):
        return status
