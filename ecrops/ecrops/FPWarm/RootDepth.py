import copy
import math


class RootDepth():
    """
    Root Depth
    """
    def setparameters(self, container):
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
            ex = container.Weather[(container.day - container.first_day).days]  # get the meteo data for current day
            p = container.Parameters  # parameters
            s = container.States  # states
            s1 = container.States1  # ???
            a = container.Auxiliary  # ???
            r = container.Rates  # rates

            s1.RootDepth = p.MaximumRootingDepth * math.log(s.DevelopmentStageCode + 1)  # log base e
            if (s1.RootDepth > p.MaximumRootingDepth):
                s1.RootDepth = p.MaximumRootingDepth


        except  Exception as e:
            print('Error in method runstep of class RootDepth:'+str(e))

        return container