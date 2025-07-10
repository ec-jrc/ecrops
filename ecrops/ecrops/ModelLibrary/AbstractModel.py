import logging
import os
from abc import ABC, abstractmethod
from ecrops.ModelEngine import ModelEngine
import pandas as pd


class AbstractModel(ABC):
    """Abstract representation of a model implementation"""

    def __init__(self, args=None, name=''):
        self.Name = name
        self.args = args

    def getName(self):
        """returns the name of the model"""
        return self.Name

    def getArgs(self):
        """returns the arguments of the model"""
        return self.args

    def initialize(self, baseDirectory, log, workflow_file, ReturnDailyDetails, ReturnDekadalDetails, PrintDailyDetails,
                   PrintDailyDetailsToFile, PrintDailyDetails_OutputFile, modelEngineClass=ModelEngine):
        """Initializes the model: initializes the ModelEngine of ECroPS and saves in the model properties the base 
        directory, the workflow file, and the arguments related to save and print the model outputs. 

       Arguments:

       :param baseDirectory: the base directory that contains the input data
       :param log: set to True to enable logging inside models
       :param workflow_file: name of the workflow XML file
       :param ReturnDailyDetails: set True to let ECroPS model to return daily simulation output data. If False, the model will return only summary output data. (better to disable for batch runs).
       :param PrintDailyDetails: set True to let ECroPS model to print daily simulation output data in the console output (better to disable for batch runs)
       :param ReturnDekadalDetails: set True to let ECroPS model to return 'dekadal' (=10 days) simulation output data. The dekadal configuration returns only the days that are considered dekadal:the 10th , the 20th and the last day of the month.
       :param PrintDailyDetailsToFile: set True to save the daily details to a file
       :param PrintDailyDetails_OutputFile: the path to save the daily details when PrintDailyDetailsToFile is true

        """
        self.baseDirectory = baseDirectory
        self.log = log
        if self.log:
            print('START read workflow file')
        self.w = modelEngineClass(os.path.join(baseDirectory, workflow_file))
        if self.log:
            print('END read workflow file')
            print("All the parameters:")
            print(self.w.getParametersListAsJson())
            print("-----------")
        self.w.ReturnDailyDetails = True
        self.w.PrintDailyDetails = False
        if ReturnDailyDetails is not None:
            self.w.ReturnDailyDetails = ReturnDailyDetails
        if ReturnDekadalDetails is not None:
            self.w.ReturnDekadalDetails = ReturnDekadalDetails
        if PrintDailyDetails is not None:
            self.w.PrintDailyDetails = PrintDailyDetails
        if PrintDailyDetailsToFile is not None:
            self.w.PrintDailyDetailsToFile = PrintDailyDetailsToFile
        if PrintDailyDetails_OutputFile is not None:
            self.TmpPrintDailyDetails_OutputFile = PrintDailyDetails_OutputFile


    def getOutputVariables(self):
        """Returns the ordered list of output variables, based on the workflow file loaded.
        For each runMode defined in the workflow file, it collects the output variables of the runMode and appends them to the list.
        It returns the output variables only of the runModes set to 'ON' in the workflow file.
        If a workflow file is not set, it gives an error, so this method should be called after the 'initialize' method """
        runModes = self.w.getRunModeNames()
        res = []
        for rm in runModes:
            rmOutoutVariable = self.w.getOutputVariables(rm)
            for v in rmOutoutVariable:
                res.append(v.name)
        return res

    @abstractmethod
    def runCycle(self, dailyData, dailyDataVariables, locationData, cropLocationData, soilData, otherVariables,
                 cropLocationDataOrder,
                 locationDataOrder, soilDataOrder, cropParameters):
        """Executes the simulation cycle of the model, using all the input data retrieved by the data loader. A further elaboration of the input data could be implemented here, before calling the initialize method of the ECroPS model.
        Typical workflow is:
         - prepare/modify the input data
         - fill the drivingVariable dictionary by uing the input data
         - for each run modes defined in the ECroPS workflow:
           - call the ModelEngine initialize method
           - call N times the ModelEngine executeStep method, where N is the length of the simulation period
           - call the ModelEngine finalize method
           - concatenate the summary output of the current run mode with the others
         -return the summary outputs and the daily details of all the run modes

        Arguments:

        :param dailyData: the array containing the daily data
        :param dailyDataVariables: a dictionary, containing for every daily data variable its position in the dailyData array. E.g.: {'temperature_max': 0, 'temperature_min': 1, 'radiation': 2, 'precipitation': 3, 'windspeed': 4, 'e0': 6, 'es0': 7, 'et0': 8, 'temperature_avg': 9}
        :param locationData: the array containing the location data
        :param cropLocationData: the array containing the crop location specific data
        :param soilData: the array containing the soil specific data
        :param otherVariables: the dictionary containing all the other variables
        :param cropLocationDataOrder: the dictionary containing the  crop location specific data order: the order gives the 0 based index position of a variable inside the cropLocationData array
        :param locationDataOrder: the dictionary containing the location data order: the order gives the 0 based index position of a variable inside the locationData array
        :param soilDataOrder: the dictionary containing the soil data order: the order gives the 0 based index position of a variable inside the soilData array
        :param cropParameters: the dictionary containing the non-location specific crop data


        Returns a tuple containing the summary output and the daily details dictionary (one entry for each run mode)
        """
        pass

    @abstractmethod
    def getOutputFileName(self, args):
        """
       Returns the name of the output file according to some simulation's arguments.
       Arguments:

       :param args: arguments of the model call
       :return: name of the output file
        """
        pass

    @abstractmethod
    def saveFinalOutput(self, data, outputFilePath):
        """Saves the final results of the simulation
         Arguments

         :param data: the output data array
         :param outputFilePath: the path of the output file to write
        """
        pass

    @abstractmethod
    def isValidLocation(self, dailyData, locationData, locationDataOrder, cropparameters, crop):
        """Checks whether the location data provided are valid. Checks are done on daily data and location data.
         Returns true if data are valid, False otherwise.
         Arguments

         :param dailydata: the array containing the daily data
         :param locationData: the array containing the location data
         :param locationDataOrder: the dictionary containing the daily data order
         :param cropparameters: crop parameters
         :param crop: crop number
        """
        return True

    @property
    def logger(self):
        loggername = "%s.%s" % (self.__class__.__module__,
                                self.__class__.__name__)
        return logging.getLogger(loggername)

    @abstractmethod
    def prepare_dekadal_output(self, args, timeseries_results):
        """Converts timeseries results into dekadal output as a pandas dataframe

           :param args: the set of arguments used to start the ModelLauncher
           :param timeseries_results: timeseries output from ECroPS
           :return: a tuple of two objects:
            - a DataFrame with results in a custom structure (for example to be converted in a SQLLDR file for CGMS23EUR)
            - the string representing the SQLLDR header associated to the dataframe
               """
        return pd.DataFrame(), ""

    @abstractmethod
    def prepare_daily_output(self, args, timeseries_results):
        """Converts timeseries results into daily output as a pandas dataframe

           :param args: the set of arguments used to start the ModelLauncher
           :param timeseries_results: timeseries output from ECroPS
           :return: a tuple of two objects:
            - a DataFrame with results in a custom structure (for example to be converted in a SQLLDR file for CGMS23EUR)
            - the string representing the SQLLDR header associated to the dataframe
               """
        return pd.DataFrame(), ""
