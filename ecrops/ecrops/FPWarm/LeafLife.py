from ecrops.Step import Step


# -----------------------------------------------
# Leaf Life
# -----------------------------------------------
from ecrops.FPWarm.GAIage import GAIage


class LeafLife(Step):
    """Leaf Life duration """

    def setparameters(self, container):
        container.WarmParameters.LeafLife = container.allparameters['LeafLife']

        return container

    def initialize(self, container):
        container.states.LeafAreaIndexAge=[]
        #initialization of LAI
        container.states.GreenLeafAreaIndex = 0
        container.states.TotalLeafAreaIndex = 0
        container.states.DeadLeafAreaIndex = 0
        container.rates.TotalLeafAreaIndexRate = 0
        container.rates.GreenLeafAreaIndexRate=0
        container.rates.DeadLeafAreaIndexRate=0
        return container



    def integrate(self, container):
        s = container.states  # states
        r = container.rates  # rates


        return container

    def getparameterslist(self):
        return {
            "LeafLife": {"Description": "Leaf duration",
                             "Type": "Number",
                             "Mandatory": "True", "UnitOfMeasure": "days"},
        }

    def getinputslist(self):
        return {

            "LeafAreaIndexAge": {"Description": "Array of HAIAge containig data on the leaf area index age", "Type": "Array of GAIage classes", "UnitOfMeasure": "",
                                     "StatusVariable": "status.states.LeafAreaIndexAge"},
            "GrowingDegreeDaysRate": {"Description": "Growing degree days rate",
                                 "Type": "Number", "UnitOfMeasure": "C",
                                 "StatusVariable": "status.rates.GrowingDegreeDaysRate"},
            "TotalLeafAreaIndex": {"Description": "Total leaf area index ",
                                   "Type": "Number",
                                   "UnitOfMeasure": "unitless",
                                   "StatusVariable": "status.states.TotalLeafAreaIndex"},
            "DeadLeafAreaIndex": {"Description": "Dead leaf area index",
                                  "Type": "Number", "UnitOfMeasure": "unitless",
                                  "StatusVariable": "status.states.DeadLeafAreaIndex"},
            "GreenLeafAreaIndex": {"Description": "Green leaf area index",
                                   "Type": "Number", "UnitOfMeasure": "unitless",
                                   "StatusVariable": "status.states.GreenLeafAreaIndex"},

        }

    def getoutputslist(self):
        return {
              "LeafAreaIndexAge": {"Description": "Array of HAIAge containig data on the leaf area index age", "Type": "Array of GAIage classes", "UnitOfMeasure": "",
                                     "StatusVariable": "status.states.LeafAreaIndexAge"},
            "DeadLeafAreaIndexRate": {"Description": "Dead leaf area index rate",
                                      "Type": "Number", "UnitOfMeasure": "unitless",
                                      "StatusVariable": "status.rates.DeadLeafAreaIndexRate"},
            "GreenLeafAreaIndexRate": {"Description": "Green leaf area index rate",
                                      "Type": "Number", "UnitOfMeasure": "unitless",
                                      "StatusVariable": "status.rates.GreenLeafAreaIndexRate"},
            "DeadLeafAreaIndex": {"Description": "Dead leaf area index",
                                       "Type": "Number", "UnitOfMeasure": "unitless",
                                       "StatusVariable": "status.states.DeadLeafAreaIndex"},
            "GreenLeafAreaIndex": {"Description": "Green leaf area index",
                                  "Type": "Number", "UnitOfMeasure": "unitless",
                                  "StatusVariable": "status.states.GreenLeafAreaIndex"},

        }

    def runstep(self, container):

        try:

            p = container.WarmParameters  # parameters
            s = container.states  # states
            r = container.rates  # rates

            for lai in s.LeafAreaIndexAge:
                if (lai.DailyGreenLeafAreaIndex > 0.0):
                    lai.GrowingDegreeDaysAssociatedToGAIunits = lai.GrowingDegreeDaysAssociatedToGAIunits + r.GrowingDegreeDaysRate

            # Add the new(today) GAI unit :
            gddVersusLAIInstance = GAIage()
            gddVersusLAIInstance.GrowingDegreeDaysAssociatedToGAIunits = 0
            gddVersusLAIInstance.DailyGreenLeafAreaIndex = r.TotalLeafAreaIndexRate
            s.LeafAreaIndexAge.append(gddVersusLAIInstance)

            # Rank the elements of the list in descending order:
            s.LeafAreaIndexAge = sorted(s.LeafAreaIndexAge, key=lambda a: a.GrowingDegreeDaysAssociatedToGAIunits,
                                        reverse=True)

            # Kill the GAI units older than the threshold:
            DeadLAI = self.LeavesAging(s.LeafAreaIndexAge, p.LeafLife, r.GrowingDegreeDaysRate)
            r.DeadLeafAreaIndexRate = DeadLAI

            # Calculates other rates:
            r.GreenLeafAreaIndexRate = r.TotalLeafAreaIndexRate - r.DeadLeafAreaIndexRate

            s.DeadLeafAreaIndex = s.DeadLeafAreaIndex + r.DeadLeafAreaIndexRate
            if s.GreenLeafAreaIndex==0.03:
                s.GreenLeafAreaIndex =0
            s.GreenLeafAreaIndex = s.GreenLeafAreaIndex + r.GreenLeafAreaIndexRate
            #s.TotalLeafAreaIndex = s.TotalLeafAreaIndex + r.TotalLeafAreaIndexRate
            if (s.DeadLeafAreaIndex < 0):
                s.DeadLeafAreaIndex = 0

            if (s.GreenLeafAreaIndex < 0):
                s.GreenLeafAreaIndex = 0

            if (s.TotalLeafAreaIndex < 0):
                s.TotalLeafAreaIndex = 0


        except  Exception as e:
            print('Error in method runstep of class LeafLife:' + str(e))

        return container


    def LeavesAging(self, list, LeafDuration, GDDtoday):
        """Leaves aging"""

        Dead = 0
        i = 0
        while True:

            if i >= len(list):
                break

            if list[i].GrowingDegreeDaysAssociatedToGAIunits + GDDtoday > LeafDuration:
                Dead = Dead + list[i].DailyGreenLeafAreaIndex
                del list[i]
                # i = i - 1
                # Memo from DF: in my opinion this line should be active, otherwise we skip one record after a record deletion.
                # We leave it commented to mimic the (here not accurate) behaviour of the original WARM Bioma.
            else:
                break

            i = i + 1

        return Dead
