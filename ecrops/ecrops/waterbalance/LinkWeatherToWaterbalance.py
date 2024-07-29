from ecrops.Step import Step
class LinkWeatherToWaterbalance(Step):
    """This step passes weather data to water balance"""

    def getparameterslist(self):
        return {}  # no parameters in this step

    def setparameters(self, status):
        return status

    def initialize(self, status):
        return self.runstep(status)

    def runstep(self, status):
        status.classicwaterbalance.rates.RAIN = status.weather.RAIN
        status.classicwaterbalance.rates.ES0 = status.weather.ES0
        status.classicwaterbalance.rates.E0 = status.weather.E0
        status.classicwaterbalance.rates.ET0 = status.weather.ET0
        return status

    def integrate(self, status):
        return status


    def getinputslist(self):
        return {

            "RAIN": {"Description": "Precipitation",
                     "Type": "Number", "UnitOfMeasure": "cm",
                     "StatusVariable": "status.weather.RAIN"},
            "E0": {"Description": "Open water evapotranspiration",
                   "Type": "Number", "UnitOfMeasure": "cm",
                   "StatusVariable": "status.weather.E0"},
            "ES0": {"Description": "Bare soil evapotranspiration",
                    "Type": "Number", "UnitOfMeasure": "cm",
                    "StatusVariable": "status.weather.ES0"},
            "ET0": {"Description": "Canopy evapotranspiration",
                    "Type": "Number", "UnitOfMeasure": "cm",
                    "StatusVariable": "status.weather.ET0"},
        }


    def getoutputslist(self):
        return {
            "RAIN": {"Description": "Precipitation",
                     "Type": "Number", "UnitOfMeasure": "cm",
                     "StatusVariable": "status.classicwaterbalance.rates.RAIN"},
            "E0": {"Description": "Open water evapotranspiration",
                   "Type": "Number", "UnitOfMeasure": "cm",
                   "StatusVariable": "status.classicwaterbalance.rates.E0"},
            "ES0": {"Description": "Bare soil evapotranspiration",
                    "Type": "Number", "UnitOfMeasure": "cm",
                    "StatusVariable": "status.classicwaterbalance.rates.ES0"},
            "ET0": {"Description": "Canopy evapotranspiration",
                    "Type": "Number", "UnitOfMeasure": "cm",
                    "StatusVariable": "status.classicwaterbalance.rates.ET0"},

        }
