from ecrops.Step import Step
class LinkWofostToHermesWaterBalance(Step):
    """This step passes Wofost data (root depth, potential transpiration) to Hermes water balance"""

    def getparameterslist(self):
        return {
            "RDI": {"Description": "Initial root depth", "Type": "Number", "Mandatory": "True", "UnitOfMeasure": "cm"},
            "RDMCR": {"Description": "Maximum root depth", "Type": "Number", "Mandatory": "True",
                      "UnitOfMeasure": "cm"}
            }

    def setparameters(self, status):
        return status

    def initialize(self, status):
        return status

    def runstep(self, status):
        status.hermeswaterbalance.states.RD = status.states.RD
        status.hermeswaterbalance.rates.TRA = status.rates.TRA
        status.hermeswaterbalance.rates.EVWMX = status.rates.EVWMX
        status.hermeswaterbalance.rates.EVSMX = status.rates.EVSMX
        status.hermeswaterbalance.rates.TRALY = status.rates.TRALY
        status.hermeswaterbalance.states.flag_crop_emerged = (status.states.DOE is not None)
        return status

    def integrate(self, status):
        status.hermeswaterbalance.states.RD = status.states.RD
        return status

    def getinputslist(self):
        return {
            # to be implemented
        }

    def getoutputslist(self):
        return {
            #to be implemented
        }
