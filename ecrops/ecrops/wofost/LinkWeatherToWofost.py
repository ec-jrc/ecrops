class LinkWeatherToWofost:
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

        status.states.DIFPP = status.astrodata.DIFPP
        status.states.DSINBE = status.astrodata.DSINBE
        status.states.SINLD = status.astrodata.SINLD
        status.states.COSLD = status.astrodata.COSLD
        status.states.DAYL = status.astrodata.DAYL
        status.states.DAYLP = status.astrodata.DAYLP
        return status

    def integrate(self, status):
        return status
