from ecrops.Printable import Printable

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
        if not hasattr(status, 'classicwaterbalance'):
            status.classicwaterbalance = Printable()
            status.classicwaterbalance.states = Printable()
            status.classicwaterbalance.rates = Printable()
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

        # from ecrops.Step import tmp_print_unit_tests
        # from ecrops.unit_tests import UnitTestXMLFilesGenerator
        # tmp_print_unit_tests(status, type(self).__name__, type(self).__module__,
        #                      "<TestSet Description=\"\"><Parameters><Parameter Name=\"RDI\" Value=\""+str(status.allparameters["RDI"])+"\" /><Parameter Name=\"RDMCR\" Value=\""+str( status.allparameters["RDMCR"])+"\" /></Parameters><Inputs><Input Name=\"status.states.RD\" Value=\""+str(status.states.RD)+"\" /><Input Name=\"status.rates.TRA\" Value=\""+str(status.rates.TRA)+"\" /><Input Name=\"status.states.DOE\" Value=\""+str(status.states.DOE)+"\" /><Input Name=\"status.rates.EVWMX\" Value=\""+str(status.rates.EVWMX)+"\" /><Input Name=\"status.rates.EVSMX\" Value=\""+str(status.rates.EVSMX)+"\" /></Inputs><Outputs><Output Name=\"status.classicwaterbalance.states.RD\" Value=\""+UnitTestXMLFilesGenerator.round_and_string(status.classicwaterbalance.states.RD,3)+"\" /><Output Name=\"status.classicwaterbalance.rates.TRA\" Value=\""+UnitTestXMLFilesGenerator.round_and_string(status.classicwaterbalance.rates.TRA,3)+"\" /><Output Name=\"status.classicwaterbalance.states.DOE\" Value=\""+UnitTestXMLFilesGenerator.round_and_string(status.classicwaterbalance.states.DOE,3)+"\" /><Output Name=\"status.classicwaterbalance.rates.EVWMX\" Value=\""+UnitTestXMLFilesGenerator.round_and_string(status.classicwaterbalance.rates.EVWMX,3)+"\" /><Output Name=\"status.classicwaterbalance.rates.EVSMX\" Value=\""+UnitTestXMLFilesGenerator.round_and_string(status.classicwaterbalance.rates.EVSMX,3)+"\" /></Outputs></TestSet>")

        return status


    def getinputslist(self):
        return {

            "RD": {"Description": "Root depth", "Type": "Number", "UnitOfMeasure": "cm",
                   "StatusVariable": "status..states.RD"},
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
