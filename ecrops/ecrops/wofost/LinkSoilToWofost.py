from ..Printable import Printable


class LinkSoilToWofost:
    """This step passes soil data to Wofost steps"""

    def getparameterslist(self):
        return {}  # no parameters in this step

    def setparameters(self, status):
        status.soildata = Printable()
        status.soildata = status.soilparameters
        status.rates = Printable()
        status.states = Printable()
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
