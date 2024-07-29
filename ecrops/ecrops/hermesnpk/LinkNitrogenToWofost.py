from ecrops.Step import Step
class LinkNitrogenToWofost(Step):
    """This step links the Nitrogen stress reduction factor to wofost"""

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

        return status



    def runstep(self,status):
        if status.states.DVS>0:
            status.assimilation.params.NSTRESS_REDUCTION_FACTOR=status.hermesnitrogenstress.REDUK # pass reduction factor to wofost
        return status


    def integrate(self,status):
        return status