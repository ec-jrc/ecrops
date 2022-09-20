class LinkWaterbalanceToWofost:
    """This step links the output of waterbalance step (soil moisture) to Wofost steps"""

    def getparameterslist(self):
        return {}  # no parameters in this step

    def setparameters(self, status):
        return status

    def initialize(self, status):
        return status

    def runstep(self, status):
        status.states.SM = status.classicwaterbalance.states.SM
        return status

    def integrate(self, status):
        return status
