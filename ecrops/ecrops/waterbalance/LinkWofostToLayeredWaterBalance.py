
class LinkWofostToLayeredWaterBalance:
    """This step passes Wofost data (root depth, potential transpiration) to layered water balance"""

    def getparameterslist(self):
        return {"RDI":{"Description":"Initial root depth","Type":"Number","Mandatory":"True","UnitOfMeasure":"cm"},
                "RDMCR": {"Description": "Maximum root depth", "Type": "Number", "Mandatory": "True",
                        "UnitOfMeasure": "cm"}
                }

    def setparameters(self,status):

        return status


    def initialize(self,status):
        status.layeredwaterbalance.parameters.RDI = status.allparameters["RDI"]
        status.layeredwaterbalance.parameters.IAIRDU = status.allparameters["IAIRDU"]
        status.layeredwaterbalance.parameters.RDMCR = status.allparameters["RDMCR"]
        return status


    def runstep(self,status):
        status.layeredwaterbalance.states.RD =status.states.RD
        status.layeredwaterbalance.rates.TRA = status.rates.TRA
        status.layeredwaterbalance.rates.EVWMX = status.rates.EVWMX
        status.layeredwaterbalance.rates.EVSMX = status.rates.EVSMX
        status.layeredwaterbalance.rates.TRALY=status.rates.TRALY
        status.layeredwaterbalance.states.flag_crop_emerged=(status.states.DOE is not None)
        return status

    def integrate(self,status):
        status.layeredwaterbalance.states.RD = status.states.RD
        return status
