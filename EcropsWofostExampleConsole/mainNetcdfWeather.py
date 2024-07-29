import time

import numpy as np
import datetime
#import the ecrops package
from ecrops.ModelEngine import ModelEngine
from ecrops.Printable import Printable
from ecrops.wofost_util.util import wind10to2
#import the netCDF4 package
from netCDF4 import Dataset

def repeat_fun(times, f, *args):
    """utility function to run the daily model many times"""
    for i in range(times): f(*args)


def move_zeros_to_right(arr):
    zero_indices = np.where(arr == 0)
    non_zero_indices = np.where(arr != 0)
    arr[:] = np.concatenate((arr[non_zero_indices], arr[zero_indices]))
    return arr



def SaveOutputToNetCDF( o, outputFileName,w):
    """
    Save the simulation data to NETCDF file
    :param o: array of data
    :param outputFileName: output file path
    param w: reference to the model
    :return:
    """
    # create netcdf from outputmatrix
    from netCDF4 import Dataset

    outFileName = outputFileName

    print("Start writing the output NETCDF file (" + outFileName + ")...\n")
    rootgrp = Dataset(outFileName, "w", format="NETCDF4")
    rootgrp.history = "Created " + time.ctime(time.time())
    rootgrp.description = "Simulation result of Wofost"

    max_soil_index = 63

    lon = rootgrp.createDimension('lon_index', maxDIMXtoLoad)
    lat = rootgrp.createDimension('lat_index', maxDIMYtoLoad)
    lons = rootgrp.createVariable('lo', 'f4', ('lon_index',))
    lats = rootgrp.createVariable('la', 'f4', ('lat_index',))
    lons.units = "degrees north"
    lats.units = "degrees east"

    lats[:] = np.arange(1, maxDIMYtoLoad + 1, 1)
    lons[:] = np.arange(1, maxDIMXtoLoad + 1, 1)

    i = 0

    runModes = w.getRunModeNames()
    for rm in runModes:
        rmOutoutVariable = w.getOutputVariables(rm)
        for v in rmOutoutVariable:

            temp = rootgrp.createVariable(v.name, "f4", ("lon_index", "lat_index",),
                                          zlib=True, least_significant_digit=2)
            temp.grid_mapping = ' '
            temp.description = v.description
            temp[ :, :] = o[ :, :, i]
            i = i + 1

    rootgrp.close()
    print("NETCDF Output file (" + outFileName + ") written\n")


def open_netcdf(fname):
    """
    Opens the specified netcdf file and returns its dataset.

    :param fname:
    :return: a netcdf4 Dataset
    """
    data = Dataset(fname, "r", format="NETCDF4")
    return data


def load_variable_data_from_NETCDF(year_from, year_to, netcdf_year_offset, filename, varname):
    """
    Read data for specific variable from input file
    :param year_from: start year to extract
    :param year_to: end year to extract
    :param netcdf_year_offset: first year of data in netcdf
    :param filename: absolute path of file to read
    :param varname: variable name
    :return: variable content
    """
    rootgrp = open_netcdf(filename)
    variable=None
    try:
        from datetime import date
        numberOfDaysBegin = (date(year_from, 1, 1) - date(netcdf_year_offset, 1, 1)).days
        numberOfDaysEnd = (date(year_to, 12, 31) - date(netcdf_year_offset, 1, 1)).days + 1
        variable = rootgrp.variables[varname][numberOfDaysBegin:numberOfDaysEnd]
        rootgrp.close()
    except Exception as e:
        print(('Could not read weather data from netcdf'))
        print(e)
        print(('Could not read weather data from netcdf. Out of index. Probably year ' + str(year_from) + ' or ' + str(
            year_to) + ' is not included in dataset or there was a memory error'))
    return variable

def load_weather_array_from_NETCDF(year_from, year_to, netcdf_year_offset, dimx, dimy, filename, variables):
    """Loads weather data from NETCDF and save to an array (365 days per year, also for leap years)

    :param year_from: start year to extract
    :param year_to: end year to extract
    :param netcdf_year_offset: first year of data in netcdf
    :param dimx: size of the X coordinate
    :param dimy: size of the Y coordinate
    :param filename: absolute path of file to read
    :param variables:names of the weather data variables in the netcdf file
    :return: a numpy array containing weather data, of size dimY-dimX-numberOfdays
    """

    # return only the first (365 * number of year) days (also for leap years)
    numberOfDays = 365 * ( year_to - year_from)
    toret = np.empty((numberOfDays, dimx, dimy, len(variables)), dtype=np.float32)

    i = 0
    for wVar in variables:
        # read variable data
        print(('Reading meteo variables:' + str(year_from) +'_' + str(year_to) +'  offset=' + str(netcdf_year_offset) +' file=' + str(filename) +' variable=' + str(wVar)))
        toret[:, :, :, i] = load_variable_data_from_NETCDF(year_from,
                                                           year_to,
                                                           netcdf_year_offset,
                                                           filename,
                                                           wVar)[0:numberOfDays, 0:dimx, 0:dimy]

        i = i + 1

    return toret.swapaxes(0, 2).swapaxes(1, 0)


#initialize wofost by reading one of the available workflow files
print('read workflow file')


#REMOVE THE COMMENT of one of the following lines to use one of the workflow files
#potential phenology simulation
#w = ModelEngine("WorkflowWofostPhenology.xml")

#potential and water limited basic simulation
#w = ModelEngine("WorkflowWofostSimple.xml")

#potential and water limited basic simulation
w = ModelEngine("WorkflowWofostSimple.xml")

#simulation run by using the partitioning factors based on the co2 effect
#w = ModelEngine("WorkflowWofostCo2Partitioning.xml")


# get all available run modes, as defined in the workflow file
runModes = w.getRunModeNames();

#set ReturnDailyDetails True to return the daily values
w.ReturnDailyDetails = True
#set PrintDailyDetails True to print the daily values in the console output
w.PrintDailyDetails = True


# define basic input data (year, location data, crop)
year = 2003 # year to run
crop = 2  # crop to run, 2=maize
lat = 39.77
lon = 8.5


# define soil data
example_soil = Printable()
example_soil.FC = 0.35 #field capacity (m^3 / m^3)
example_soil.WP = 0.19 #wilting point (m^3 / m^3)
example_soil.SAT = 0.45 #saturation (m^3 / m^3)
example_soil.thickess = 200  # soil max thickness in cm
initial_water_content = (example_soil.FC - example_soil.WP) * example_soil.thickess/100 #initial water content (water content per soil depth)


# define sowing date
sowingDate = 105  # day of the year from 1 to 365

# define co2concentrations for the years to run. Values should be provided for every year to run.
Co2Concentrations = {}
Co2Concentrations["1959"]=360 #co2 contentration in ppm for year 1959
Co2Concentrations["1960"]=361 #co2 contentration in ppm for year 1960
Co2Concentrations[str(year)]=400 #co2 contentration in ppm for year 'year'

# read weather data from a Netcdf file
filename='weatherSample_2003.nc'
maxDIMXtoLoad = 9 #the sample netcdf file contains data for a 9x5 grid for 365 days (year 2003, from 1st Jan to 31st Dec)
maxDIMYtoLoad = 5
variables=['temperature_max','temperature_min','radiation','precipitation','windspeed','e0','es0','et0']
weather_matrix = load_weather_array_from_NETCDF(year - 1, year, year, maxDIMXtoLoad, maxDIMYtoLoad,filename, variables )

outputarray = []

#for all the grid cells
for x in range(maxDIMXtoLoad):
    for y in range(maxDIMYtoLoad):
        #from the array of weather data, read the weather of the single location to simulate
        timeDependantVariables = weather_matrix[x,y,:]

        #changing unit of measure when necessary
        timeDependantVariables[:, 0] = timeDependantVariables[:, 0]  # tmax (C)
        timeDependantVariables[:, 1] = timeDependantVariables[:, 1]  # tmin (C)
        timeDependantVariables[:, 2] = timeDependantVariables[:, 2] * 1000  # rad (KJ => J)
        timeDependantVariables[:, 3] = timeDependantVariables[:, 3] / 10.  # rain (mm  =>  cm)
        timeDependantVariables[:, 4] = wind10to2(timeDependantVariables[:, 4])  # wind  (m/s)
        timeDependantVariables[:, 5] = timeDependantVariables[:, 5] / 10.  # E0 #cm (mm  =>  cm)
        timeDependantVariables[:, 6] = timeDependantVariables[:, 6] / 10.  # ES0 #cm (mm  =>  cm)
        timeDependantVariables[:, 7] = timeDependantVariables[:, 7] / 10.  # ET0 #cm (mm  =>  cm)

        timeDependantVariableColumn = {'TEMP_MAX': 0, 'TEMP_MIN': 1, 'IRRAD': 2, 'RAIN': 3, 'WIND': 4, 'E0': 5, 'ES0': 6, 'ET0': 7}

        weather = timeDependantVariables


        # set Wofost parameter values. For parameters explanation see Wofost documentation here: https://wofost.readthedocs.io/en/latest/
        parameters = {'VERNRTB': [0.0, 0.0], 'DVSI': 0.0, 'DLO': -99.0, 'PlantDensity': 10,
                      'DTSMTB': [0.0, 0.0, 8.0, 0.0, 34.0, 26.0, 44.0, 26.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                 0.0, 0.0, 0.0, 0.0], 'TSUM2': 858, 'RRI': 2.2, 'DLC': -99.0, 'CVL': 0.68, 'CVO': 0.7,
                      'FOTB': [0.0, 0.0, 0.33, 0.0, 0.88, 0.0, 0.95, 0.0, 1.1, 0.5, 1.34, 1.0, 2.0, 1.0, 0.0, 0.0, 0.0,
                               0.0, 0.0, 0.0], 'KDIF': 0.5, 'TSUMEM': 125, 'TEFFMX': 30.0, 'RMS': 0.006, 'DEPNR': 5,
                      'SLATB': [0.0, 0.00236, 0.78, 0.0008, 2.0, 0.0008, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                0.0, 0.0, 0.0, 0.0, 0.0], 'RMR': 0.006, 'VERNSAT': 0.0,
                      'AMAXTB': [0.0, 70.0, 1.25, 70.0, 1.5, 63.0, 1.75, 49.0, 2.0, 21.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                 0.0, 0.0, 0.0, 0.0],
                      'RFSETB': [0.0, 1.0, 1.5, 1.0, 1.75, 0.75, 2.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                 0.0, 0.0, 0.0], 'CVR': 0.69, 'KDIFTB': [0.0, 0.5, 2.0, 0.5], 'RML': 0.011, 'SPA': 0.0,
                      'IDSL': 0.0,
                      'TMNFTB': [5.0, 0.0, 8.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                 0.0, 0.0, 0.0], 'RMO': 0.005, 'VERNBASE': 0.0,
                      'RDRRTB': [0.0, 0.0, 1.5, 0.0, 1.5001, 0.02, 2.0, 0.02, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                 0.0, 0.0, 0.0, 0.0], 'RGRLAI': 0.0294, 'Q10': 2.0, 'IAIRDU': 0.0, 'VERNDVS': 0.0,
                      'EFF': [0.0, 0.45, 1.0, 0.45], 'SSA': [0.0, 0.0, 1.0, 0.0], 'SPAN': 35, 'TBASEM': 4.0,
                      'PERDL': 0.01, 'IOX': 0, 'TBASE': 12.65, 'LAIEM': 0.04836,
                      'TMPFTB': [0.0, 0.01, 9.0, 0.05, 16.0, 0.8, 18.0, 0.94, 20.0, 1.0, 30.0, 1.0, 36.0, 0.95, 42.0,
                                 0.56, 0.0, 0.0, 0.0, 0.0], 'RDI': 10.0, 'USEVERNALISATION': 0, 'CFET': 1.0,
                      'CVS': 0.658, 'SSATB': [0.0, 0.0, 2.0, 0.0], 'TSUM1': 788,
                      'FLTB': [0.0, 0.62, 0.33, 0.62, 0.88, 0.15, 0.95, 0.15, 1.1, 0.1, 1.2, 0.0, 2.0, 0.0, 0.0, 0.0,
                               0.0, 0.0, 0.0, 0.0], 'TDWI': 137, 'RDMCR': 100.0, 'DVSEND': 2.0,
                      'FRTB': [0.0, 0.4, 0.1, 0.37, 0.2, 0.34, 0.3, 0.31, 0.4, 0.27, 0.5, 0.23, 0.6, 0.19, 0.7, 0.15,
                               0.8, 0.1, 0.9, 0.06, 1.0, 0.0, 2.0, 0.0], 'EFFTB': [0.0, 0.45, 40.0, 0.45],
                      'FSTB': [0.0, 0.38, 0.33, 0.38, 0.88, 0.85, 0.95, 0.85, 1.1, 0.4, 1.2, 0.0, 2.0, 0.0, 0.0, 0.0,
                               0.0, 0.0, 0.0, 0.0],
                      'RDRSTB': [0.0, 0.0, 1.5, 0.0, 1.5001, 0.02, 2.0, 0.02, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                 0.0, 0.0, 0.0, 0.0]}






        #get the number of available weather days
        numberOfWeatherDays = weather.shape[0]

        # set driving variables
        drivingVariables = {
                            # Set to True to enable Co2Effect on crop growth
                            'ConsiderCo2Effect': False,

                            #Co2 related parameters
                            'Co2FertReference': 369,
                            'Co2Concentrations': Co2Concentrations,
                            'Co2FertSlope': 0.18,

                            #number of days to execute the model
                            'DURATION': numberOfWeatherDays,

                            #soil dta
                            'SOIL_MOISTURE_CONTENT_FC': example_soil.FC,
                            'SOIL_MOISTURE_CONTENT_WP': example_soil.WP,
                            'SOIL_MOISTURE_CONTENT_SAT': example_soil.SAT,
                            'WAV': initial_water_content,
                            'DEPTH': example_soil.thickess,

                            #start doy of crop (sowing date)
                            'START_DOY': sowingDate,

                            #year to run
                            'YEAR': year,

                            #crop to run
                            'Crop': crop,

                            #lat/lon data
                            'LON': lon,
                            'LAT': lat
                            }

        print("\nRUNNING for sowing date " + str(sowingDate) + " and year " + str(year))



        #for each of the running mode defined in the configuration file
        for rm in runModes:
            print("\nINFO: Start to run on " + rm + " mode");



            status = None
            #initialize the model
            import datetime
            #set the initial value of day as first January of the year. This is the first day for which we have available weather data
            first_day = datetime.datetime(drivingVariables['YEAR'], 1, 1)
            #set the start of the simulation 2 days before the sowing
            simulation_start_day = first_day + datetime.timedelta(days=(int(int(drivingVariables['START_DOY']) - 2)))
            #set the end of the simulation DURATION days after the sowing
            simulation_end_day = simulation_start_day + datetime.timedelta(days=int(drivingVariables['DURATION']))
            #initialize the model with weather data, driving variables, parameters and the days to define the simulation cycle
            status = w.initialize(weather,timeDependantVariableColumn, drivingVariables, parameters,
                                    first_day=first_day,
                                    simulation_start_day=simulation_start_day,
                                    simulation_end_day=simulation_end_day)

            # execute the model calling the execute step method for the number of weather days
            repeat_fun(numberOfWeatherDays, w.executeStep, status, rm)

            # get the summary model output
            runOutputSummary, runOutputDailyDetails = w.finalize(status, rm)



            #the first time, initialize the output array
            if x==0 and y==0:
                if len(runOutputSummary) > 0:
                    numberOfOutputVariables = len(runOutputSummary)
                    outputarray = np.zeros([maxDIMXtoLoad, maxDIMYtoLoad, numberOfOutputVariables], dtype=np.float32)
            #save summary result to results array
            outputarray[x,y]=runOutputSummary

            print("\n--Simulation results-- run mode "+str(rm))
            # print output variables names
            print(w.getOutputVariablesNames(rm))
            # print output variables values
            print(runOutputSummary)

            print("\nEnd run " + rm + " mode")
print("\nSaving the grid output to netcdf")
SaveOutputToNetCDF(outputarray,'NetcdfOutputFile.nc',w)