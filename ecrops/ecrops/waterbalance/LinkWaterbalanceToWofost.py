from ecrops.Step import Step
class LinkWaterbalanceToWofost(Step):
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


    def getinputslist(self):
        return {

            "SM": {"Description": "Actual volumetric soil moisture content",
                   "Type": "Number", "UnitOfMeasure": "",
                   "StatusVariable": "status.classicwaterbalance.states.SM"},
        }


    def getoutputslist(self):
        return {
               "SM": {"Description": "Actual volumetric soil moisture content",
                   "Type": "Number", "UnitOfMeasure": "",
                   "StatusVariable": "status.states.SM"},

        }
