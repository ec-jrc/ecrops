import math


class NUptake:
    """N Uptake by plant from Hermes. Copied from file crop.go rows 410- 500
    N-content functions (critical and optimal N-content)
    Functions for GEHMAX  and GEHMIN either depending on development (PHYLLO) or above ground biomass (OBMAS)

    Main inputs
    NGEFKT = crop N-content function no. (critical and max. N-contents).… (number between 1 and 9, it is a sort of paramtrization set)
    PHYLLO = cumulative development effective temperature sum (°C days)

    Outputs
    GEHMAX   = maximum N content (drives N uptake) (kg N/kg biomass)
    GEHMIN   = critical N-content of above ground biomass (below = N-Stress) (kg N/kg biomass)
    """


    def getparameterslist(self):
        return {
            "NGEFKT": {
                "Description": "number of N function is set in crop parameter file",
                "Type": "Number",
                "Mandatory": "True",
                "UnitOfMeasure": ""}
        }

    def setparameters(self, status):


        return status

    def initialize(self, status):

        status.hermesnuptake.subd = 1  # number of subdivisions in a day
        status.hermesnuptake.wdt = 1  # fraction of day ( the time step of one day is sometimes reduced when water flux becommes too high)

        # initialize outputs
        status.hermesnuptake.GEHMAX = 0  # maximum N content (drives N uptake) (kg N/kg biomass)
        status.hermesnuptake.GEHMIN = 0  # critical N-content of above ground biomass (below = N-Stress) (kg N/kg biomass)

        return status

    def runstep(self, status):
        g = status.hermesnuptake


        if hasattr(status.hermesnitrogen,'FRUCHT') and status.hermesnitrogen.FRUCHT =="WW ":
            status.hermesnuptake.params.NGEFKT  = 1  # crop N-content function no. (critical and max. N-contents). value 1 is for winter wheat
        else:#TODO: manage other crops
            status.hermesnuptake.params.NGEFKT  = 2 #crop N-content function no. (critical and max. N-contents). # value 2 is for maize


        # number of N function is set in crop parameter file
        if status.hermesnuptake.params.NGEFKT == 1:
            if g.PHYLLO < 200:
                g.GEHMIN = .0415
                g.GEHMAX = .06
            else:
                if g.FRUCHT == "WR " or g.FRUCHT == "SG ":
                    g.GEHMIN = 5.1 * math.exp (-.00165 * g.PHYLLO) / 100
                    g.GEHMAX = 8.0 * math.exp (-.0017 * g.PHYLLO) / 100
                else:
                    g.GEHMIN = 5.5 * math.exp (-.0014 * g.PHYLLO) / 100
                    g.GEHMAX = 8.1 * math.exp (-.00147 * g.PHYLLO) / 100


        else:
            if status.hermesnuptake.params.NGEFKT == 2:
                if g.PHYLLO < 263:
                    g.GEHMIN = 0.035
                else:
                    g.GEHMIN = 0.035 - 0.024645 * math.pow(
                        (1 - math.exp (-(g.PHYLLO - 152.30391 * math.log(1 - math.sqrt(2) / 2) - 438.63545) / 152.30391)),
                        2)

                if g.PHYLLO < 142:
                    g.GEHMAX = 0.049
                else:
                    g.GEHMAX = 0.049 - 0.037883841 * math.pow(
                        (1 - math.exp (-(g.PHYLLO - 201.50354 * math.log(1 - math.sqrt(2) / 2) - 385.8318) / 201.50354)),
                        2)

            else:
                if status.hermesnuptake.params.NGEFKT == 3:
                    if g.OBMAS < 1000:
                        g.GEHMAX = 0.06
                        g.GEHMIN = 0.045
                    else:
                        g.GEHMAX = 0.06 * math.pow((g.OBMAS / 1000), (-0.25))
                        g.GEHMIN = 0.045 * math.pow((g.OBMAS / 1000), (-0.25))

                else:
                    if status.hermesnuptake.params.NGEFKT == 4:
                        if (g.OBMAS + g.WORG[3]) < 1000:
                            g.GEHMAX = 0.06
                            g.GEHMIN = 0.045
                        else:
                            g.GEHMAX = 0.0285 + 0.0403 * math.exp (-0.26 * (g.OBMAS + g.WORG[3]) / 1000)
                            g.GEHMIN = 0.0135 + 0.0403 * math.exp (-0.26 * (g.OBMAS + g.WORG[3]) / 1000)

                    else:
                        if status.hermesnuptake.params.NGEFKT == 5:
                            g.WORG= [0,0,0,0]#davidefuma WORG used unly for tuber... it is the organ below surface. We set it to zero

                            if (status.hermesnitrogen.OBMAS + g.WORG[3]) < 1100:
                                g.GEHMAX = 0.06
                                g.GEHMIN = 0.045
                            else:
                                g.GEHMAX = 0.06 * math.pow(((status.hermesnitrogen.OBMAS + g.WORG[3]) / 1000), 0.5294)
                                g.GEHMIN = 0.046694 * math.pow(((status.hermesnitrogen.OBMAS + g.WORG[3]) / 1000), 0.5294)

                        else:
                            if status.hermesnuptake.params.NGEFKT == 6:
                                if g.PHYLLO < 400:
                                    g.GEHMIN = .0415
                                    g.GEHMAX = .06
                                else:
                                    g.GEHMIN = 5.5 * math.exp (-.0007 * g.PHYLLO) / 100
                                    g.GEHMAX = 8.1 * math.exp (-.0007 * g.PHYLLO) / 100

                            else:
                                if status.hermesnuptake.params.NGEFKT == 7:
                                    if g.OBMAS < 1000:
                                        g.GEHMAX = 0.0615
                                        g.GEHMIN = 0.0448
                                    else:
                                        g.GEHMAX = 0.0615 * math.pow((g.OBMAS / 1000), (-0.25))
                                        g.GEHMIN = 0.0448 * math.pow((g.OBMAS / 1000), (-0.25))

                                else:
                                    if status.hermesnuptake.params.NGEFKT == 8:
                                        if g.PHYLLO < 200 * g.tendsum / 1260:
                                            g.GEHMIN = .0415
                                            g.GEHMAX = .06
                                        else:
                                            # correction factor fr development depending functions for variety specific temperature sums
                                            dvkor = 1 / ((g.tendsum - 200) / (1260 - 200))
                                            if g.FRUCHT[g.AKF.Index] == "WR " or g.FRUCHT[g.AKF.Index] == "SG ":
                                                g.GEHMIN = 5.1 * math.exp (-.00165 * dvkor * g.PHYLLO) / 100
                                                g.GEHMAX = 8.0 * math.exp (-.0017 * dvkor * g.PHYLLO) / 100
                                            else:
                                                g.GEHMIN = 5.5 * math.exp (-.0014 * dvkor * g.PHYLLO) / 100
                                                g.GEHMAX = 8.1 * math.exp (-.00147 * dvkor * g.PHYLLO) / 100


                                    else:
                                        if status.hermesnuptake.params.NGEFKT == 9:
                                            if (g.OBMAS + g.WORG[3]) < 1000:
                                                g.GEHMAX = 0.06
                                                g.GEHMIN = 0.045
                                            else:
                                                g.GEHMAX = 0.0285 + 0.0403 * math.exp (-0.26 * g.OBMAS / 1000)
                                                g.GEHMIN = 0.0135 + 0.0403 * math.exp (-0.26 * g.OBMAS / 1000)

        return status

    def integrate(self, status):
        return status
