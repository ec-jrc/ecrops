import logging
from abc import ABC, abstractmethod


class AbstractDataLoader(ABC):
    """Abstract representation of a data loader class"""

    def __init__(self, args=None, Name=''):
        self.Name = Name
        self.args = args

    def getName(self):
        """returns the data loader name"""
        return self.Name

    def getArgs(self):
        """returns the data loader arguments"""
        return self.args

    @abstractmethod
    def getDailyData(self):
        """returns an array containing the input daily data (for example the weather data). Shape of daily data should be: NUM_SEASONS x NUM_LOCATIONS x NUM_DAYS X NUM_DAILY_VARIABLES"""
        pass

    @abstractmethod
    def getDailyDataVariables(self):
        """returns the names of input daily data (for example the weather data) in a dictionary. The key of the dictionary is the name of the variable, the value is its position in the array returned by getDailyData"""
        pass

    @abstractmethod
    def getLocationData(self):
        """returns an array containing the fixed location data (for example the soil data). Shape of location data should be: NUM_CROPS x NUM_SEASONS x NUM_LOCATIONS x NUM_LOCATION_VARIABLES"""
        pass

    @abstractmethod
    def getLocationDataOrder(self):
        """returns the list of variables contained in Location data and their zero-based position index in the array returned by getLocationData()"""
        pass

    @abstractmethod
    def getCropParameters(self):
        """returns the non-location specific crop parameters"""
        pass

    @abstractmethod
    def getCropLocationData(self):
        """returns an array containing the location specific crop data and parameters. Shape of crop location data should be: NUM_CROPS x NUM_SEASONS x NUM_LOCATIONS x NUM_CROP_LOCATION_VARIABLES"""
        pass

    @abstractmethod
    def getCropLocationDataOrder(self):
        """returns the list of variables contained in Crop Location Data and their zero-based position index in the
        array returned by getCropLocationData() """
        pass

    @abstractmethod
    def getSoilData(self):
        """returns an array containing the soil specific data. Shape of soil data should be: NUM_LOCATIONS x NUM_SOIL_PER_LOCATION, NUM_LAYERS x NUM_SOIL_VARIABLES """
        return self.soilData

    @abstractmethod
    def getSoilDimensionSize(self):
        """returns the size of the soil dimension"""
        if len(self.soilData) > 0:
            return self.soilData.shape[1]
        else:
            return 1

    @abstractmethod
    def getSoilDataOrder(self):
        """returns the list of variables contained in Soil Data and their zero-based position index in the array
        returned by getSoilData() """
        return self.soilDataOrder

    @abstractmethod
    def getOtherVariables(self):
        """return a dictionary containing other auxiliary variables"""
        pass

    @property
    def logger(self):
        loggername = "%s.%s" % (self.__class__.__module__,
                                self.__class__.__name__)
        return logging.getLogger(loggername)
