class LinkWofostToWaterbalance:
    """This step passes Wofost data (root depth, potential transpiration) to water balance"""

    def getparameterslist(self):
        return {
            "RDI": {"Description": "Initial root depth", "Type": "Number", "Mandatory": "True", "UnitOfMeasure": "cm"},
            "RDMCR": {"Description": "Maximum root depth", "Type": "Number", "Mandatory": "True",
                      "UnitOfMeasure": "cm"}
            }

    def setparameters(self, status):
        return status

    def initialize(self, status):
        status.classicwaterbalance.states.RDI = status.allparameters["RDI"]
        status.classicwaterbalance.states.RDMCR = status.allparameters["RDMCR"]
        return status

    def runstep(self, status):
        status.classicwaterbalance.states.RD = status.states.RD
        status.classicwaterbalance.rates.TRA = status.rates.TRA
        status.classicwaterbalance.states.DOE = status.states.DOE
        status.classicwaterbalance.rates.EVWMX = status.rates.EVWMX
        status.classicwaterbalance.rates.EVSMX = status.rates.EVSMX
        return status

    def integrate(self, status):
        status.classicwaterbalance.states.RD = status.states.RD
        return status
