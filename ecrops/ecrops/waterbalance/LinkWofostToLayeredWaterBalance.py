from ecrops.Printable import Printable

from ecrops.Step import Step
class LinkWofostToLayeredWaterBalance(Step):
    """This step passes Wofost data (root depth, potential transpiration) to layered water balance"""

    def getparameterslist(self):
        return {
            "RDI": {"Description": "Initial root depth", "Type": "Number", "Mandatory": "True", "UnitOfMeasure": "cm"},
            "RDMCR": {"Description": "Maximum root depth", "Type": "Number", "Mandatory": "True",
                      "UnitOfMeasure": "cm"},
            "IAIRDU": {"Description": "Switch airducts on (1) or off (0)", "Type": "Number", "Mandatory": "True",
                       "UnitOfMeasure": "unitless"},
            }

    def setparameters(self, status):
        if not hasattr(status,'layeredwaterbalance'):
            status.layeredwaterbalance = Printable()
            status.layeredwaterbalance.states = Printable()
            status.layeredwaterbalance.rates = Printable()
            status.layeredwaterbalance.parameters = Printable()
        status.layeredwaterbalance.parameters.RDI = status.allparameters["RDI"]
        status.layeredwaterbalance.parameters.IAIRDU = status.allparameters["IAIRDU"]
        status.layeredwaterbalance.parameters.RDMCR = status.allparameters["RDMCR"]
        return status

    def initialize(self, status):

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
        # p=status.layeredwaterbalance.parameters
        # from ecrops.Step import tmp_print_unit_tests
        # from ecrops.unit_tests import UnitTestXMLFilesGenerator
        # tmp_print_unit_tests(status, type(self).__name__, type(self).__module__,
        #                      "<TestSet Description=\"\"><Parameters><Parameter Name=\"RDI\" Value=\""+str(p.RDI)+"\" /><Parameter Name=\"RDMCR\" Value=\""+str(p.RDMCR)+"\" /></Parameters><Inputs><Input Name=\"status.states.RD\" Value=\""+str(status.states.RD)+"\" /><Input Name=\"status.rates.TRA\" Value=\""+str(status.rates.TRA)+"\" /><Input Name=\"status.states.DOE\" Value=\""+str(status.states.DOE)+"\" /><Input Name=\"status.rates.EVWMX\" Value=\""+str(status.rates.EVWMX)+"\" /><Input Name=\"status.rates.EVSMX\" Value=\""+str(status.rates.EVSMX)+"\" /><Input Name=\"status.rates.TRALY\" Value=\""+str(status.rates.TRALY)+"\" /></Inputs><Outputs><Output Name=\"status.layeredwaterbalance.states.RD\" Value=\""+UnitTestXMLFilesGenerator.round_and_string(status.layeredwaterbalance.states.RD,3)+"\" /><Output Name=\"status.layeredwaterbalance.rates.TRA\" Value=\""+UnitTestXMLFilesGenerator.round_and_string(status.layeredwaterbalance.rates.TRA,3)+"\" /><Output Name=\"status.layeredwaterbalance.states.flag_crop_emerged\" Value=\""+UnitTestXMLFilesGenerator.round_and_string(status.layeredwaterbalance.states.flag_crop_emerged,3)+"\" /><Output Name=\"status.layeredwaterbalance.rates.EVWMX\" Value=\""+UnitTestXMLFilesGenerator.round_and_string(status.layeredwaterbalance.rates.EVWMX,3)+"\" /><Output Name=\"status.layeredwaterbalance.rates.EVSMX\" Value=\""+UnitTestXMLFilesGenerator.round_and_string(status.layeredwaterbalance.rates.EVSMX,3)+"\" /><Output Name=\"status.layeredwaterbalance.rates.TRALY\" Value=\""+UnitTestXMLFilesGenerator.round_and_string(status.layeredwaterbalance.rates.TRALY,3)+"\" /></Outputs></TestSet>")

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
