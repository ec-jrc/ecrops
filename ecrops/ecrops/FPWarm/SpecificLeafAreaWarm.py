
class SpecificLeafAreaWarm:
    """
    Specific leaf area.
    Reference: Confalonieri, R., Gusberti, D., Acutis, M., 2006. Comparison of WOFOST, CropSyst and WARM for
    simulating rice growth (Japonica type – short cycle varieties). Italian Journal of Agrometeorology, 3, 7-16
    """
    def setparameters(self, container):
        return container

    def initialize(self, container):
        return container

    def integrate(self, container):
        return container

    def getparameterslist(self):
        return {
            "SpecificLeafAreaAtTillering": {"Description": "Specific leaf area at tillering",
                                                "Type": "Number",
                                                "Mandatory": "True", "UnitOfMeasure": "m2 kg-1"},
            "SpecificLeafAreaAtEmergence": {"Description": "Specific leaf area at emergence",
                                            "Type": "Number",
                                            "Mandatory": "True", "UnitOfMeasure": "m2 kg-1"},
        }

    def runstep(self, container):

        try :
            ex = container.Weather[(container.day - container.first_day).days]  # get the meteo data for current day
            p = container.Parameters  # parameters
            s = container.States  # states
            s1 = container.States1  # ???
            a = container.Auxiliary  # ???
            r = container.Rates  # rates

            if s.DevelopmentStageCode >= 1 and s.DevelopmentStageCode < 3:
                s1.SpecificLeafArea = self.SLAfromDVS(s.DevelopmentStageCode, p.SpecificLeafAreaAtTillering,
                                                      p.SpecificLeafAreaAtEmergence) * 1000

                r.TotalLeafAreaIndexRate = r.LeavesBiomassRate / 10 * (s1.SpecificLeafArea / 1000)

                s1.TotalLeafAreaIndex = s.TotalLeafAreaIndex + r.TotalLeafAreaIndexRate

            # move the s1 status to the states variable
            #container.States = copy.deepcopy(s1)

        except  Exception as e:
            print('Error in method runstep of class SpecificLeafAreaWarm:'+str(e))

        return container


    def SLAfromDVS(self, DVS, SpecificLeafAreaAtTillering, SpecificLeafAreaAtEmergence):
        """
        Specific Lead Area estimation from the Developement stage
        """

        if DVS >= 1 and DVS <= 1.35:
            result = ((SpecificLeafAreaAtTillering - SpecificLeafAreaAtEmergence) / 0.1225) * \
                     (((DVS - 1) ** 2)) + SpecificLeafAreaAtEmergence

        else:
            if DVS > 1.35 and DVS <= 3:
                result = SpecificLeafAreaAtTillering

            else:
                result = 0

        result = result / 1000

        return result