from ecrops.Step import Step
class LinkWeatherToHermesRootDepth(Step):
    """This step passes weather data to Hermes root depth step"""

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
        status.hermesrootdepth.cumuldegreeedays=0
        return self.runstep(status)



    def runstep(self,status):
        status.hermesrootdepth.cumuldegreeedays += status.weather.TEMP
        return status


    def integrate(self,status):
        return status