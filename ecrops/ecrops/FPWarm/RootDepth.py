from ecrops.Step import Step
import math


class RootDepth(Step):
    """
    Root Depth
    """
    def setparameters(self, container):
        if not hasattr(container, 'WarmParameters'):
            from ecrops.Printable import Printable
            container.WarmParameters = Printable()
        container.WarmParameters.MaximumRootingDepth = container.allparameters['MaximumRootingDepth']

        return container

    def initialize(self, container):
        return container

    def integrate(self, container):
        return container

    def getparameterslist(self):
        return {
            "MaximumRootingDepth": {"Description": "Maximum rooting depth",
                                                    "Type": "Number",
                                                    "Mandatory": "True", "UnitOfMeasure": "cm"},
        }

    def runstep(self, container):

        try :

            p = container.WarmParameters  # parameters
            s = container.states  # states
            r = container.rates  # rates

            s.RootDepth = p.MaximumRootingDepth * math.log(s.DevelopmentStageCode + 1)  # log base e
            if s.RootDepth > p.MaximumRootingDepth:
                s.RootDepth = p.MaximumRootingDepth


        except  Exception as e:
            print('Error in method runstep of class RootDepth:'+str(e))

        return container

    def getinputslist(self):
        return {

            "DevelopmentStageCode": {"Description": "Development stage", "Type": "Number", "UnitOfMeasure": "unitless",
                                     "StatusVariable": "status.states.DevelopmentStageCode"},

        }

    def getoutputslist(self):
        return {

            "RootDepth": {"Description": "Root depth ",
                            "Type": "Number", "UnitOfMeasure": "cm",
                            "StatusVariable": "status.states.RootDepth"},
        }