from ecrops.Step import Step
class LinkWeatherToHermesWaterBalance(Step):
    """This step passes weather data to Hermes water balance"""

    def getparameterslist(self):
        return {}  # no parameters in this step

    def setparameters(self, status):
        return status

    def initialize(self, status):
        return self.runstep(status)

    def runstep(self, status):
        status.hermeswaterbalance.rates.RAIN = status.weather.RAIN
        status.hermeswaterbalance.rates.ES0 = status.weather.ES0
        status.hermeswaterbalance.rates.E0 = status.weather.E0
        status.hermeswaterbalance.rates.ET0 = status.weather.ET0
        status.hermeswaterbalance.FLUSS0 = status.weather.RAIN - status.weather.E0  # in cm
        return status

    def integrate(self, status):
        return status

    def getinputslist(self):
        return {
            # to be implemented
        }

    def getoutputslist(self):
        return {
            #to be implemented
        }
