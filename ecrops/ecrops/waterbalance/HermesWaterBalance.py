import numpy as np
from ecrops.Step import Step

class HermesWaterBalance(Step):
    """Waterbalance from Hermes model (Keserbaum)
    
    WATER MODEL acc.to BURNS drainage when field capacity is exceeded upward movement for evaporation acc.to Groot (1987)

    Used VARIABLEs:
     thickness layer (standard 10cm):           dz
     FIELD CAPACITY (cm^3/cm^3):                W(z)
     no. of layers:                             N
     WATER CONTENT of LAYERS (cm^3/cm^3):       WG(,)
     Absolute WATER PER LAYER (cm = 10mm/m^2):  WASSER
     INFILTRATION(+) resp. EVAPORATION(-)(cm):  FLUSS0
     Depth of TILE DRAIN  (dm)                  DRAIDEP
     Drainfactor (fraction) if > FC             DRAIFAK

    Q1(I) = water flux through the bottom of layer I (cm/d)
    FLUSS0 = INFILTRATION(+) resp. EVAPORATION(-)(cm)

    Description from: K.C. Kersebaum / Application of a simple management model to simulate water and nitrogen
    dynamics  / 1994. To describe water balance in soil a simple plate theory model is used. Therefore the soil
    profile has been divided into layers of 30 cm thickness. In the present version a profile of 120 cm is simulated.
    The capacity parameters required by the model as 9, the water content at field capacity and 9, the water content
    at wilting point are derived automatically within the model from the soil texture class of the layer modified by
    organic matter content, hydromorphic patterns and bulk density class. The texture classes and values are taken
    from tables of AG Bodenkunde (1982). Capillary rise from the groundwater table is taken into account by using
    constant flux rates (mm day- ‘) dependent on texture class and distance between the regarded layer and the
    groundwater table. These values, also taken from AG Bodenkttnde (19821, are defined for a water conten? of 70% of
    usable field capacity. The model determines from the bottom to the top the first layer where water content is
    below 70% usabIe field capacity. Then using the distance of this layer to the groundwater table the flux is
    calculated as a steady state flux through all the soil layers below. Potential evapotranspiration (PET) is
    calculated by a simple empirical method developed by Haude (1955) using plant-speciCc coefficients from Heger (
    1978). This methc!rl requires only daily vapour pressure deficit as input data. The percentage of potential
    evaporation (E,,) can be calculated from the actual leaf area index (Goudriaan, 1977) using  Epot = PETexp(
    -0SLAI) (1)  Potential evaporation is reduced to actual  evaporation ,dependent on soil water content in the
    upper layer which is distributed over depth with an exponential function over depth according to van Keulen (
    1975). Water uptake by plants is calculated based on potential transpiration and distributed over depth relating
    uptake to the root length density and a soil water-dependent root efficiency factor (Groot, 1987). Potential
    transpiration is reduced if water supply is insufficient. Water deficits can partly be compensated in rooted
    layers below.

    """

    def getparameterslist(self):
        return {

        }

    def getinputslist(self):
        return {
            # to be implemented
        }

    def getoutputslist(self):
        return {
            #to be implemented
        }

    def setparameters(self, status):
        return status

    def initialize(self, status):
        status.hermeswaterbalance.subd = 1  # number of subdivisions in a day
        status.hermeswaterbalance.wdt = 1  # fraction of day ( the time step of one day is sometimes reduced when water flux becommes too high)
        status.hermeswaterbalance.GlobalVarsMain = status.soildata['HermesGlobalVarsMain']

        return status

    def runstep(self, status):
        WATER = np.zeros((2, 21), dtype=float)
        g = status.hermeswaterbalance.GlobalVarsMain
        l = status.hermeswaterbalance.WaterSharedVars
        if status.hermeswaterbalance.subd == 1:

            for i in range(0, g.N):
                if g.TP[i] > (g.WG[0][i] - g.WMIN[i]) * g.DZ[i]:
                    if g.WG[0][i] < g.WMIN[i]:
                        g.TP[i] = 0
                    else:
                        g.TP[i] = (g.WG[0][i] - g.WMIN[i]) * g.DZ[i]

                WATER[0][i] = g.WG[0][i] * g.DZ[i] - g.TP[i] * status.hermeswaterbalance.wdt

        else:
            for i in range(0, g.N):
                g.WG[0][i] = g.WG[1][i]
                WATER[0][i] = g.WG[0][i] * g.DZ[i] - g.TP[i] * status.hermeswaterbalance.wdt

        g.QDRAIN = 0
        if status.hermeswaterbalance.FLUSS0 > 0:
            a = status.hermeswaterbalance.FLUSS0 * status.hermeswaterbalance.wdt
            g.Q1[0] = a
            # ------------------------ Infiltration------------------------
            for k1 in range(1, g.N + 1):
                k1INdex = k1 - 1
                b = a + WATER[0][k1INdex]
                a = b - g.W[k1INdex] * g.DZ[k1INdex]
                if a < 0:
                    WATER[1][k1INdex] = b
                    g.Q1[k1] = 0
                    for k2 in range(k1 + 1, g.N + 1):
                        k2Index = k2 - 1
                        WATER[1][k2Index] = WATER[0][k2Index]
                        g.Q1[k2] = 0
                    break

                else:
                    if k1 == g.DRAIDEP:
                        g.Q1[k1] = (1 - g.DRAIFAK) * a
                        g.QDRAIN = g.DRAIFAK * a
                        a = g.Q1[k1]
                    else:
                        g.Q1[k1] = a

                    WATER[1][k1INdex] = g.W[k1INdex] * g.DZ[k1INdex]
                    g.Q1[k1] = a




        # --------------------------Evaporation - -----------------------
        else:
            if status.hermeswaterbalance.FLUSS0 < 0:
                a = abs(status.hermeswaterbalance.FLUSS0) * status.hermeswaterbalance.wdt
                a1 = a
                g.Q1[0] = 0
                for k1 in range(0, g.N):
                    l.LIMIT[k1] = WATER[0][k1] - l.EV[k1] * status.hermeswaterbalance.wdt
                    if l.LIMIT[k1] < (g.WMIN[k1] / 3) * g.DZ[k1]:
                        l.EV[k1 + 1] = l.EV[k1 + 1] + (l.EV[k1] - WATER[0][k1] + g.WMIN[k1] / 3 * g.DZ[k1])
                        l.EV[k1] = WATER[0][k1] - g.WMIN[k1] / 3 * g.DZ[k1]
                        l.LIMIT[k1] = g.WMIN[k1] / 3 * g.DZ[k1]

                    vcap = WATER[0][k1] - l.LIMIT[k1]
                    wlost = 0
                    if vcap > a1:
                        wlost = a1
                        WATER[1][k1] = WATER[0][k1] - wlost
                        g.Q1[k1 + 1] = 0
                        for k2 in range(k1 + 1, g.N):
                            WATER[1][k2] = WATER[0][k2]
                            g.Q1[k2 + 1] = 0

                        break
                    else:
                        wlost = vcap
                        a1 = a1 - vcap
                        g.Q1[k1 + 1] = -a1

                    WATER[1][k1] = WATER[0][k1] - wlost

            else:  # FLUSS0 == 0
                for i in range(0, g.N):
                    WATER[1][i] = WATER[0][i]
                    g.Q1[i + 1] = 0

        for i in range(0, g.N):
            if WATER[1][i] / g.DZ[i] > g.W[i]:
                sink = WATER[1][i] - g.W[i] * g.DZ[i]
                WATER[1][i] = g.W[i] * g.DZ[i]
                WATER[1][i + 1] = WATER[1][i + 1] + sink
                g.Q1[i + 1] = g.Q1[i + 1] + sink

        return status

    def integrate(self, status):
        return status
