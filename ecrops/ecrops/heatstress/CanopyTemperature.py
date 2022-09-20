from ..Printable import Printable


class CanopyTemperature:
    """
    Calculate canopy temperature from air temperature. For now the canopy temperature is set equal to the maximum
    temperature. This should be implemented using the correct algorithm
    """

    def getparameterslist(self):
        return {
        }

    def setparameters(self, status):
        status.canopytemperature = Printable()
        status.canopytemperature.params = Printable()
        return status

    def initialize(self, status):
        status.canopytemperature.canopytemperature = 0
        return status

    def runstep(self, status):
        status.canopytemperature.canopytemperature = status.states.TEMP_MAX
        return status

    def integrate(self, status):
        return status
