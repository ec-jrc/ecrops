import copy
import math
from GAIage import GAIage


# -----------------------------------------------
# Leaf Life
# -----------------------------------------------
class LeafLife():
    """Leaf Life duration """

    def setparameters(self, container):
        return container

    def initialize(self, container):
        return container

    def integrate(self, container):
        return container

    def getparameterslist(self):
        return {
            "LeafDuration": {"Description": "Leaf duration",
                             "Type": "Number",
                             "Mandatory": "True", "UnitOfMeasure": "days"},
        }

    def runstep(self, container):

        try:
            ex = container.Weather[(container.day - container.first_day).days]  # get the meteo data for current day
            p = container.Parameters  # parameters
            s = container.States  # states
            s1 = container.States1  # ???
            a = container.Auxiliary  # ???
            r = container.Rates  # rates

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
            DeadLAI = self.LeavesAging(s.LeafAreaIndexAge, p.LeafDuration, r.GrowingDegreeDaysRate)
            r.DeadLeafAreaIndexRate = DeadLAI

            # Calculates other rates:
            r.GreenLeafAreaIndexRate = r.TotalLeafAreaIndexRate - r.DeadLeafAreaIndexRate

            s1.DeadLeafAreaIndex = s.DeadLeafAreaIndex + r.DeadLeafAreaIndexRate
            s1.GreenLeafAreaIndex = s.GreenLeafAreaIndex + r.GreenLeafAreaIndexRate
            s1.TotalLeafAreaIndex = s.TotalLeafAreaIndex + r.TotalLeafAreaIndexRate
            if (s1.DeadLeafAreaIndex < 0):
                s1.DeadLeafAreaIndex = 0

            if (s1.GreenLeafAreaIndex < 0):
                s1.GreenLeafAreaIndex = 0

            if (s1.TotalLeafAreaIndex < 0):
                s1.TotalLeafAreaIndex = 0

            s1.LeafAreaIndexAge = s.LeafAreaIndexAge


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
