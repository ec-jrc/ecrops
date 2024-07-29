from ecrops.Step import Step
class LinkWofostToWaterbalance(Step):
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
        }


    def getoutputslist(self):
        return {
            "RD": {"Description": "Root depth", "Type": "Number", "UnitOfMeasure": "cm",
                   "StatusVariable": "status.classicwaterbalance.states.RD"},
            "TRA": {"Description": "Actual transpiration rate from the plant canopy", "Type": "Number",
                    "UnitOfMeasure": "cm/day",
                    "StatusVariable": "status.classicwaterbalance.rates.TRA"},
            "DOE": {"Description": "Doy of emergence", "Type": "Number", "UnitOfMeasure": "doy",
                    "StatusVariable": "status.classicwaterbalance.states.DOE"},
            "EVWMX": {"Description": "Maximum evaporation rate from an open water surface", "Type": "Number",
                      "UnitOfMeasure": "cm/day",
                      "StatusVariable": "status.classicwaterbalance.rates.EVWMX"},
            "EVSMX": {"Description": "Maximum evaporation rate from a wet soil surface", "Type": "Number",
                      "UnitOfMeasure": "cm/day",
                      "StatusVariable": "status.classicwaterbalance.rates.EVSMX"},

        }
