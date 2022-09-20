from .SoilLayerHermes import SoilLayerHermes

class LinkSoilToHermesRootDepth:
    """This step passes soil data to Hermes root depth step"""

    def getparameterslist(self):
        return {}  # no parameters in this step

    def setparameters(self, status):
        return status

    def initialize(self, status):
        il = 0
        for layer in status.soilparameters["SOIL_LAYERS"]:
            l = SoilLayerHermes()
            l.lowerBoundary = status.soilparameters["SOIL_LAYERS"][il].LBSL
            if il > 0:
                l.upperBoundary = status.soilparameters["SOIL_LAYERS"][il - 1].LBSL
            else:
                l.upperBoundary = 0
            status.hermesrootdepth.hermes_roots_layer_data.append(l)
            il += 1
        return status

    def runstep(self, status):
        return status

    def integrate(self, status):
        return status
