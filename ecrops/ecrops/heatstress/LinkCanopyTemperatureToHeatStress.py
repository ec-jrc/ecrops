from ecrops.Step import Step
class LinkCanopyTemperatureToHeatStress(Step):
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

    def getinputslist(self):
        return {

            "canopytemperature": {"Description": "Canopy temperature",
                                  "Type": "Number", "UnitOfMeasure": "C",
                                  "StatusVariable": "status.canopytemperature.canopytemperature"},
        }

    def getoutputslist(self):
        return {

            "canopytemperature": {"Description": "Canopy temperature",
                                  "Type": "Number", "UnitOfMeasure": "C",
                                  "StatusVariable": "status.heatstress.canopytemperature"},

        }

