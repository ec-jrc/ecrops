
from ecrops.Step import Step
class LinkWeatherToNitrogen(Step):
    """This step passes weather data to nitrogen steps"""

    def getparameterslist(self):
        return {}#no parameters in this step

    def setparameters(self,status):

        return status

    def getinputslist(self):
        return {
            # to be implemented
        }

    def getoutputslist(self):
        return {
            #to be implemented
        }


    def initialize(self,status):

        return self.runstep(status)



    def runstep(self,status):
        status.hermestransport.FLUSS0 = status.weather.RAIN - status.weather.E0  # in cm. todo: check if it the right evapotr.
        return status


    def integrate(self,status):
        return status