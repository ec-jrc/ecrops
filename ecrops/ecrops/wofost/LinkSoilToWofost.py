from ecrops.Step import Step
from ..Printable import Printable


class LinkSoilToWofost(Step):
    """This step passes soil data to Wofost steps"""

    def getparameterslist(self):
        return {}  # no parameters in this step

    def setparameters(self, status):
        status.soildata = Printable()
        status.soildata = status.soilparameters

        return status

    def initialize(self, status):

        # present only in case of layered water balance
        if 'SOIL_LAYERS' in status.soildata:
            status.states.SOIL_LAYERS = status.soildata['SOIL_LAYERS']
            status.states.NSL = len(
                status.states.SOIL_LAYERS)  # 0 for non layered water balance and evaporation calculation. >0 for specifying the eveporation calculation for NSL layers
        else:
            # present only in case of hermes  water balance
            if 'HermesGlobalVarsMain' in status.soildata:
                status.states.HermesGlobalVarsMain = status.soildata['HermesGlobalVarsMain']
                status.states.NSL = status.states.HermesGlobalVarsMain.N
            else:
                status.states.SOIL_LAYERS = None
                status.states.NSL = 0
        return status

    def runstep(self, status):
        return status

    def integrate(self, status):
        return status

    def getinputslist(self):
        return {

            "soilparameters": {"Description": "Soil data input", "Type": "Dictionary", "UnitOfMeasure": "-",
                         "StatusVariable": "status.soilparameters"},
        }

    def getoutputslist(self):
        return {

            "SOIL_LAYERS": {"Description": "Soil layers data (only in case of multi layer soil data)", "Type": "List",
                            "UnitOfMeasure": "-",
                            "StatusVariable": "status.states.SOIL_LAYERS"},

            "NSL": {"Description": "Number of soil layers (only in case of multi layer soil data)", "Type": "Number",
                    "UnitOfMeasure": "-",
                    "StatusVariable": "status.states.NSL"},
            "HermesGlobalVarsMain": {
                "Description": "Container of Hermes related soil data (only in case of multi layer Hermes model soil data)",
                "Type": "Number",
                "UnitOfMeasure": "-",
                "StatusVariable": "status.states.HermesGlobalVarsMain"},

        }
