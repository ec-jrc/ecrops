from ecrops.Printable import Printable

from ecrops.Step import Step
class LinkWeatherToLayeredWaterBalance(Step):
    """This step passes weather data to layered water balance"""

    def getparameterslist(self):
        return {}#no parameters in this step

    def setparameters(self,status):
        if not hasattr(status,'layeredwaterbalance'):
            status.layeredwaterbalance = Printable()
            status.layeredwaterbalance.states = Printable()
            status.layeredwaterbalance.rates = Printable()
            status.layeredwaterbalance.parameters = Printable()
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
                     "StatusVariable": "status.layeredwaterbalance.rates.RAIN"},
            "E0": {"Description": "Open water evapotranspiration",
                   "Type": "Number", "UnitOfMeasure": "cm",
                   "StatusVariable": "status.layeredwaterbalance.rates.E0"},
            "ES0": {"Description": "Bare soil evapotranspiration",
                    "Type": "Number", "UnitOfMeasure": "cm",
                    "StatusVariable": "status.layeredwaterbalance.rates.ES0"},
            "ET0": {"Description": "Canopy evapotranspiration",
                    "Type": "Number", "UnitOfMeasure": "cm",
                    "StatusVariable": "status.layeredwaterbalance.rates.ET0"},

        }
