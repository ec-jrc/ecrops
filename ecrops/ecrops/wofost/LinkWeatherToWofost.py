from ecrops.Step import Step
class LinkWeatherToWofost(Step):
    """This step passes weather data to Wofost steps"""

    def getparameterslist(self):
        return {}  # no parameters in this step

    def setparameters(self, status):
        return status

    def initialize(self, status):
        return self.runstep(status)

    def runstep(self, status):
        status.states.TEMP = status.weather.TEMP
        status.states.TEMP_MAX = status.weather.TEMP_MAX
        status.states.TEMP_MIN = status.weather.TEMP_MIN
        status.states.DTEMP = status.weather.DTEMP
        status.states.IRRAD = status.weather.IRRAD
        status.states.TMINRA = status.weather.TMINRA
        status.states.ET0 = status.weather.ET0
        status.states.E0 = status.weather.E0
        status.states.ES0 = status.weather.ES0
        status.states.RAIN = status.weather.RAIN
        status.states.SD = status.weather.SD
        status.states.DIFPP = status.astrodata.DIFPP
        status.states.DSINBE = status.astrodata.DSINBE
        status.states.SINLD = status.astrodata.SINLD
        status.states.COSLD = status.astrodata.COSLD
        status.states.DAYL = status.astrodata.DAYL
        status.states.DAYLP = status.astrodata.DAYLP
        return status

    def integrate(self, status):
        return status

    def getinputslist(self):
        return {

            "RAIN": {"Description": "Precipitation",
                     "Type": "Number", "UnitOfMeasure": "cm",
                     "StatusVariable": "status.weather.RAIN"},
            "WIND": {"Description": "Windspeed",
                     "Type": "Number", "UnitOfMeasure": "m/s",
                     "StatusVariable": "status.weather.WIND"},

            "E0": {"Description": "Open water evapotranspiration",
                   "Type": "Number", "UnitOfMeasure": "cm",
                   "StatusVariable": "status.weather.E0"},
            "ES0": {"Description": "Bare soil evapotranspiration",
                    "Type": "Number", "UnitOfMeasure": "cm",
                    "StatusVariable": "status.weather.ES0"},
            "ET0": {"Description": "Canopy evapotranspiration",
                    "Type": "Number", "UnitOfMeasure": "cm",
                    "StatusVariable": "status.weather.ET0"},

            "IRRAD": {"Description": "Daily shortwave radiation",
                      "Type": "Number", "UnitOfMeasure": "J/(m2 day) ",
                      "StatusVariable": "status.weather.IRRAD"},
            "TEMP_MIN": {"Description": "Minimum temperature",
                         "Type": "Number", "UnitOfMeasure": "C",
                         "StatusVariable": "status.weather.TEMP_MIN"},
            "TEMP_MAX": {"Description": "Maximum temperature",
                         "Type": "Number", "UnitOfMeasure": "C",
                         "StatusVariable": "status.weather.TEMP_MAX"},
            "TEMP": {"Description": "Average daily temperature",
                     "Type": "Number", "UnitOfMeasure": "C",
                     "StatusVariable": "status.weather.TEMP"},

            "TMINRA": {"Description": "7-days running mean of minimum temperature",
                       "Type": "Number", "UnitOfMeasure": "C",
                       "StatusVariable": "status.weather.TMNSAV"},
            "DAYL": {"Description": " Astronomical daylength (base = 0 degrees)",
                     "Type": "Number", "UnitOfMeasure": "h",
                     "StatusVariable": "status.astrodata.DAYL"},
            "DAYLP": {"Description": " Astronomical daylength (base =-4 degrees)",
                      "Type": "Number", "UnitOfMeasure": "h",
                      "StatusVariable": "status.astrodata.DAYLP"},

            "DIFPP": {"Description": "Diffuse irradiation perpendicular to direction of light",
                      "Type": "Number", "UnitOfMeasure": "J m-2 s-1",
                      "StatusVariable": "status.astrodata.DIFPP"},
            "DSINBE": {"Description": " Daily total of effective solar height ",
                       "Type": "Number", "UnitOfMeasure": "s",
                       "StatusVariable": "status.astrodata.DSINBE"},
            "SINLD": {"Description": "Seasonal offset of sine of solar height ",
                      "Type": "Number", "UnitOfMeasure": "unitless",
                      "StatusVariable": "status.astrodata.SINLD"},
            "COSLD": {"Description": "Amplitude of sine of solar height   ",
                      "Type": "Number", "UnitOfMeasure": "unitless",
                      "StatusVariable": "status.astrodata.COSLD"},
        }

    def getoutputslist(self):
        return {

            "RAIN": {"Description": "Precipitation",
                     "Type": "Number", "UnitOfMeasure": "cm",
                     "StatusVariable": "status.states.RAIN"},
            "WIND": {"Description": "Windspeed",
                     "Type": "Number", "UnitOfMeasure": "m/s",
                     "StatusVariable": "status.states.WIND"},

            "E0": {"Description": "Open water evapotranspiration",
                   "Type": "Number", "UnitOfMeasure": "cm",
                   "StatusVariable": "status.states.E0"},
            "ES0": {"Description": "Bare soil evapotranspiration",
                    "Type": "Number", "UnitOfMeasure": "cm",
                    "StatusVariable": "status.states.ES0"},
            "ET0": {"Description": "Canopy evapotranspiration",
                    "Type": "Number", "UnitOfMeasure": "cm",
                    "StatusVariable": "status.states.ET0"},

            "IRRAD": {"Description": "Daily shortwave radiation",
                      "Type": "Number", "UnitOfMeasure": "J/(m2 day) ",
                      "StatusVariable": "status.states.IRRAD"},
            "TEMP_MIN": {"Description": "Minimum temperature",
                         "Type": "Number", "UnitOfMeasure": "C",
                         "StatusVariable": "status.states.TEMP_MIN"},
            "TEMP_MAX": {"Description": "Maximum temperature",
                         "Type": "Number", "UnitOfMeasure": "C",
                         "StatusVariable": "status.states.TEMP_MAX"},
            "TEMP": {"Description": "Average daily temperature",
                     "Type": "Number", "UnitOfMeasure": "C",
                     "StatusVariable": "status.states.TEMP"},
            "DTEMP": {"Description": "Max temperature plus average daily temperature, divided by 2", "Type": "Number",
                      "UnitOfMeasure": "C",
                      "StatusVariable": "status.states.DTEMP"},

            "TMINRA": {"Description": "7-days running mean of minimum temperature",
                       "Type": "Number", "UnitOfMeasure": "C",
                       "StatusVariable": "status.states.TMNSAV"},
            "DAYL": {"Description": " Astronomical daylength (base = 0 degrees)",
                     "Type": "Number", "UnitOfMeasure": "h",
                     "StatusVariable": "status.states.DAYL"},
            "DAYLP": {"Description": " Astronomical daylength (base =-4 degrees)",
                      "Type": "Number", "UnitOfMeasure": "h",
                      "StatusVariable": "status.states.DAYLP"},

            "DIFPP": {"Description": "Diffuse irradiation perpendicular to direction of light",
                      "Type": "Number", "UnitOfMeasure": "J m-2 s-1",
                      "StatusVariable": "status.states.DIFPP"},
            "DSINBE": {"Description": " Daily total of effective solar height ",
                       "Type": "Number", "UnitOfMeasure": "s",
                       "StatusVariable": "status.states.DSINBE"},
            "SINLD": {"Description": "Seasonal offset of sine of solar height ",
                      "Type": "Number", "UnitOfMeasure": "unitless",
                      "StatusVariable": "status.states.SINLD"},
            "COSLD": {"Description": "Amplitude of sine of solar height   ",
                      "Type": "Number", "UnitOfMeasure": "unitless",
                      "StatusVariable": "status.states.COSLD"},
        }
