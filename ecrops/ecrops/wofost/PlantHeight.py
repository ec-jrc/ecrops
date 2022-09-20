import math

from ..Printable import Printable


class PlantHeight:
    """Class for calculating plant height as function of maximum height and DVS (CERES approach).
    """

    def getparameterslist(self):
        return {
            "MaximumPlantHeight": {"Description": "Maximum Plant Height", "Type": "Number",
                                   "Mandatory": "True", "UnitOfMeasure": "cm"}

        }

    def setparameters(self, status):
        status.plantheight = Printable()
        status.plantheight.params = Printable()
        status.plantheight.params.MaximumPlantHeight = status.MaximumPlantHeight
        return status

    def initialize(self, status):
        status.plantheight.PlantHeight = 0
        return status

    def runstep(self, status):
        p = status.plantheight.params
        if status.states.DVS > 1:
            status.plantheight.PlantHeight = p.MaximumPlantHeight / (1 + math.exp(-12 * (status.states.DVS - 0.5)))
        return status

    def integrate(self, status):
        return status
