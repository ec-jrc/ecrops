from ecrops.Step import Step
class LinkWofostToLayeredWaterBalance(Step):
    """This step passes Wofost data (root depth, potential transpiration) to layered water balance"""

    def getparameterslist(self):
        return {
            "RDI": {"Description": "Initial root depth", "Type": "Number", "Mandatory": "True", "UnitOfMeasure": "cm"},
            "RDMCR": {"Description": "Maximum root depth", "Type": "Number", "Mandatory": "True",
                      "UnitOfMeasure": "cm"}
            }

    def setparameters(self, status):
        return status

    def initialize(self, status):
        status.layeredwaterbalance.parameters.RDI = status.allparameters["RDI"]
        status.layeredwaterbalance.parameters.IAIRDU = status.allparameters["IAIRDU"]
        status.layeredwaterbalance.parameters.RDMCR = status.allparameters["RDMCR"]
        return status

    def runstep(self, status):
        status.layeredwaterbalance.states.RD = status.states.RD
        status.layeredwaterbalance.rates.TRA = status.rates.TRA
        status.layeredwaterbalance.rates.EVWMX = status.rates.EVWMX
        status.layeredwaterbalance.rates.EVSMX = status.rates.EVSMX
        status.layeredwaterbalance.rates.TRALY = status.rates.TRALY
        status.layeredwaterbalance.states.flag_crop_emerged = (status.states.DOE is not None)
        return status

    def integrate(self, status):
        status.layeredwaterbalance.states.RD = status.states.RD
        return status

    def getinputslist(self):
        return {

            "RD": {"Description": "Root depth", "Type": "Number", "UnitOfMeasure": "cm",
                   "StatusVariable": "status.states.RD"},
            "TRA": {"Description": "Actual transpiration rate from the plant canopy", "Type": "Number",
                    "UnitOfMeasure": "cm/day",
                    "StatusVariable": "status.rates.TRA"},
            "DOE": {"Description": "Doy of emergence", "Type": "Number", "UnitOfMeasure": "doy",
                    "StatusVariable": "status.states.DOE"},
            "EVWMX": {"Description": "Maximum evaporation rate from an open water surface", "Type": "Number",
                      "UnitOfMeasure": "cm/day",
                      "StatusVariable": "status.rates.EVWMX"},
            "EVSMX": {"Description": "Maximum evaporation rate from a wet soil surface", "Type": "Number",
                      "UnitOfMeasure": "cm/day",
                      "StatusVariable": "status.rates.EVSMX"},
            "TRALY": {
                "Description": "Array of actual transpiration rates of different layers (one value per layer, only in case of multi layer soil model)",
                "Type": "ArrayOfNumbers",
                "UnitOfMeasure": "cm/day",
                "StatusVariable": "status.rates.TRALY"},
        }

    def getoutputslist(self):
        return {
            "RD": {"Description": "Root depth", "Type": "Number", "UnitOfMeasure": "cm",
                   "StatusVariable": "status.layeredwaterbalance.states.RD"},
            "TRA": {"Description": "Actual transpiration rate from the plant canopy", "Type": "Number",
                    "UnitOfMeasure": "cm/day",
                    "StatusVariable": "status.layeredwaterbalance.rates.TRA"},
            "flag_crop_emerged": {"Description": "True if crop emerged", "Type": "Boolean", "UnitOfMeasure": "-",
                                  "StatusVariable": "status.layeredwaterbalance.states.flag_crop_emerged"},
            "EVWMX": {"Description": "Maximum evaporation rate from an open water surface", "Type": "Number",
                      "UnitOfMeasure": "cm/day",
                      "StatusVariable": "status.layeredwaterbalance.rates.EVWMX"},
            "EVSMX": {"Description": "Maximum evaporation rate from a wet soil surface", "Type": "Number",
                      "UnitOfMeasure": "cm/day",
                      "StatusVariable": "status.layeredwaterbalance.rates.EVSMX"},
            "TRALY": {
                "Description": "Array of actual transpiration rates of different layers (one value per layer, only in case of multi layer soil model)",
                "Type": "ArrayOfNumbers",
                "UnitOfMeasure": "cm/day",
                "StatusVariable": "status.layeredwaterbalance.rates.TRALY"},

        }
