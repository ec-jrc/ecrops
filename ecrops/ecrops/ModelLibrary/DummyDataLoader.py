import numpy as np
from ecrops.ModelLibrary.AbstractDataLoader import AbstractDataLoader


class DummyDataLoader(AbstractDataLoader):
    """trivial implementation of AbstractDataLoader"""
    def __init__(self, args=None, Name='DummyDataLoader'):
        self.Name=Name
        self.args=args

    def getDailyData(self):
        return np.empty((0, 0, 0, 0, 0), dtype=np.float32)

    def getDailyDataVariables(self):
        return ""

    def getLocationData(self):
        return [0]

    def getLocationDataOrder(self):
        return {}

    def getCropParameters(self):
        return {}

    def getCropLocationData(self):
        return None


    def getCropLocationDataOrder(self):
        return {}


    def getOtherVariables(self):
        return None

    def getSoilData(self):
        return self.soilData

    def getSoilDimensionSize(self):
        if len(self.soilData) > 0:
            return self.soilData.shape[1]
        else:
            return 1

    def getSoilDataOrder(self):
        return self.soilDataOrder
