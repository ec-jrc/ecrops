class LinkWeatherToLayeredWaterBalance:
    """This step passes weather data to layered water balance"""

    def getparameterslist(self):
        return {}#no parameters in this step

    def setparameters(self,status):
        return status



    def initialize(self,status):
        return self.runstep(status)

    def runstep(self,status):
        status.layeredwaterbalance.rates.RAIN = status.weather.RAIN
        status.layeredwaterbalance.rates.ES0 = status.weather.ES0
        status.layeredwaterbalance.rates.E0 = status.weather.E0
        status.layeredwaterbalance.rates.ET0 = status.weather.ET0
        return status


    def integrate(self,status):
        return status