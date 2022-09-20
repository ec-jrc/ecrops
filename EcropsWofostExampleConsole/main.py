import numpy as np
import datetime
#import the ecrops package
from ecrops.ModelEngine import ModelEngine
from ecrops.Printable import Printable
from ecrops.wofost_util.util import wind10to2


def repeat_fun(times, f, *args):
    """utility function to run the daily model many times"""
    for i in range(times): f(*args)


def ExtractWeather(allrecords, fromdate, todate, firstyear):
    """Utility function to extract the right slice of weather data, knowing the first year of weather

    Arguments:
    allrecords -- the weather data array
    fromdate -- start date to extract
    todate -- end date to extract
    firstyear -- first year of weather in the file (it is given that weather starts the 1st of Jan)
    """
    firstday = datetime.datetime(firstyear, 1, 1)
    f = (fromdate - firstday).days
    t = (todate - firstday).days
    return allrecords[f:t, ]

# initialize wofost by reading the workflow file
print('read workflow file')
w = ModelEngine("WorkflowWofostSimple.xml")

# get all available run modes, as defined in the workflow file
runModes = w.getRunModeNames();

#set ReturnDailyDetails True to return the daily values
w.ReturnDailyDetails = True
#set PrintDailyDetails True to print the daily values in the console output
w.PrintDailyDetails = True


# define basic input data (year, location data, crop)
year = 1980 # year to run
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

# define co2concentrations for the years to run
Co2Concentrations = {}
Co2Concentrations["1959"]=360 #co2 contentration in ppm for year 1959
Co2Concentrations["1960"]=361 #co2 contentration in ppm for year 1960
Co2Concentrations[str(year)]=400 #co2 contentration in ppm for year 'year'

# read weather data from CSV file
timeDependantVariables = np.genfromtxt('SampleWeatherSantaLucia1959-2019.csv', delimiter=';', skip_header=1, dtype=float)
#changing unit of measure when necessary
timeDependantVariables[:, 0] = timeDependantVariables[:, 0]  # tmax (C)
timeDependantVariables[:, 1] = timeDependantVariables[:, 1]  # tmin (C)
timeDependantVariables[:, 2] = timeDependantVariables[:, 2] * 1000  # rad (KJ => J)
timeDependantVariables[:, 3] = timeDependantVariables[:, 3] / 10.  # rain (mm  =>  cm)
timeDependantVariables[:, 4] = wind10to2(timeDependantVariables[:, 4])  # wind  (m/s)
timeDependantVariables[:, 5] = timeDependantVariables[:, 5]  # hum  (%)
timeDependantVariables[:, 6] = timeDependantVariables[:, 6] / 10.  # E0 #cm (mm  =>  cm)
timeDependantVariables[:, 7] = timeDependantVariables[:, 7] / 10.  # ES0 #cm (mm  =>  cm)
timeDependantVariables[:, 8] = timeDependantVariables[:, 8] / 10.  # ET0 #cm (mm  =>  cm)

timeDependantVariableColumn = {'TEMP_MAX': 0, 'TEMP_MIN': 1, 'IRRAD': 2, 'RAIN': 3, 'WIND': 4, 'RH': 5, 'E0': 6, 'ES0': 7, 'ET0': 8}

# extract current year weather from weather array, from 1 Jan to 31 Dec of year
firstYearInWeatherData = 1959 #first year in weather data file
weather = ExtractWeather(timeDependantVariables, datetime.datetime(year, 1, 1),
                         datetime.datetime(year, 12, 31), firstYearInWeatherData)


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
    runOutput = w.finalize(status, rm)

    print("\n--Simulation results-- run mode "+str(rm))
    # print output variables names
    print(w.getOutputVariablesNames(rm))
    # print output variables values
    print(runOutput)

    print("\nEnd run " + rm + " mode")
