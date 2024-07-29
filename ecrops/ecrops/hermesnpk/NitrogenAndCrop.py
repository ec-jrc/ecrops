# -*- coding: utf-8 -*-
#
# This component was derived from Hermes model (by professor Kurt Christian Kersebaum (Leibniz Centre for Agricultural Landscape Research)) and traslated and adapted by JRC for the eCrops framework
# European Commission, Joint Research Centre, March 2023



import numpy as np

from ..Printable import Printable
import math
from ecrops.Step import Step

class NitrogenAndCrop(Step):
    """ Main nitrogen process and plant assimilation from Hermes, taken from file crop.go"""

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

    def calculateQREZ(self, veloc, tempsum, tsumbase):
        qrez = max(math.pow((0.081476 + math.exp(-veloc * (tempsum + tsumbase))), 1.8), 0.0409)
        return qrez

    def initialize(self, status):

        status.hermesnitrogen.subd = 1  # number of subdivisions in a day
        status.hermesnitrogen.wdt = 1  # fraction of day ( the time step of one day is sometimes reduced when water flux becommes too high)

        # initialize outputs
        status.hermesnitrogen.WRAD = np.zeros(21, dtype=float)  # root radius for every level
        status.hermesnitrogen.WULAEN = 0  # rooth length
        status.hermesnitrogen.WULAE = np.zeros(21, dtype=float)  # Wulae(i) = root length from layer 0 to depth I
        status.hermesnitrogen.WULAE2 = np.zeros(21, dtype=float)  # root length for every level
        status.hermesnitrogen.WUDICH = np.zeros(21, dtype=float)  # root length density for every level
        status.hermesnitrogen.FL = np.zeros(21, dtype=float)  # root surface for every level
        status.hermesnitrogen.MASS = np.zeros(21, dtype=float)  # the daily Nuptake in each layer I by mass flow
        status.hermesnitrogen.DIFF = np.zeros(21, dtype=float)  # N diffusion for every layer
        status.hermesnitrogen.SUMDIFF = 0  # total N diffusion (DIFF)
        status.hermesnitrogen.NMINSUM = 0  # total N mineralization
        status.hermesnitrogen.TRNSUM = 0  # the sum of MASS(I) over the rooting depth (If TRNSUM is not sufficient to cover DTGESN the maximum N transport to the roots by diffusion DIFF is added until DTGESN is fulfilled. )
        status.hermesnitrogen.PE = np.zeros(21, dtype=float)  # N-uptake for every layer
        status.hermesnitrogen.SUMPE = 0  # sum of PE (N-uptake in biomass) for every layer in current step
        status.hermesnitrogen.PESUM = 0  # total N uptake in biomass crop at the beginning of the day
        status.hermesnitrogen.N_IN_WU = 0  # total N uotake in roots
        status.hermesnitrogen.MASSUM = 0
        status.hermesnitrogen.DIFFSUM = 0
        status.hermesnitrogen.rootdepth_hermes = 0  # root depth in cm
        status.hermesnitrogen.MAX_N_IN_PLANT = 0
        status.hermesnitrogen.DTGESN = 0
        status.hermesnitrogen.CUMULATED_WUMM = 0  # cumulated N in dead roots

        return status

    def runstep(self, status):

        g = status.hermesnitrogen

        DZ = 10

        # if no biomass, return
        if g.OBMAS == 0:
            return status

        # at the first day biomass > 0
        if g.OBALT == 0:
            # File crop.go rows 236-245: calculation of PESUM (= sum of Nitrogen content in the plant at the beginning of the day
            # for ZR = sugar beets or K = potatoes
            if g.FRUCHT == "ZR " or g.FRUCHT == "K  ":
                status.hermesnitrogen.PESUM = (g.OBMAS * g.GEHOB + (g.WUMAS + g.WORG[3]) * g.WUGEH)
            else:
                status.hermesnitrogen.PESUM = (g.OBMAS * g.GEHOB + g.WUMAS * g.WUGEH)

            for i in range(0, g.N):
                g.WUDICH[i] = 0

        # File crop.go rows lines 368-387: “accelaration of development by water and nutrient stress (empirical) (7.11.07 aus Ottawa)”. If there is water stress ( TRREL <1) or Nitrogen stress (REDUK<1) there is an acceleration of phenology development (!).
        Nprog = 0
        if g.FRUCHT == "ZR " or g.FRUCHT == "SM ":
            # no acceleration by N-Stress for ZR and SM (silage maize)
            Nprog = 1
        else:
            Nprog = 1 + math.pow((1 - status.hermesnitrogenstress.REDUK), 2)

        # File crop.go rows lines 409-502:  calculation of critical (status.hermesnuptake.GEHMIN) and optimal (status.hermesnuptake.GEHMAX) N-content based on development (PHYLLO) or above ground biomass (OBMAS) using some hardcoded N content functions
        # this code is in file NUptake.py

        # File crop.go rows lines 502-525: calculation of Nitrogen stress (REDUK)
        # this code is in file NitrogenStress.py

        # File crop.go rows lines 535-560: calculation of storage organ biomass. In this calculation the Nitrogen stress (REDUK) is used
        # we should modify wofost to take it into consideration #TODO

        # File crop.go rows lines 623-627: calculation of DTGESN= the N demand per day limited by the uptake capacity per cm root. So it represents the daily maximum possible uptake, which is then limited by soil N availability.
        if g.FRUCHT == "ZR " or g.FRUCHT == "K  ":
            DTGESN = (status.hermesnuptake.GEHMAX * g.OBMAS + (g.WUMAS + g.WORG[3]) * g.WGMAX - g.PESUM)
        else:
            DTGESN = (status.hermesnuptake.GEHMAX * g.OBMAS + g.WUMAS * g.WGMAX - g.PESUM)

        g.MAX_N_IN_PLANT = status.hermesnuptake.GEHMAX * g.OBMAS + g.WUMAS * g.WGMAX
        g.DTGESN = DTGESN
        # File crop.go rows lines 637-643: limit  DTGESN calculated before between 0 and 6 kg N/ha
        # limitation to 6 kg N/ha daily N-uptake
        if DTGESN > 6:
            DTGESN = 6
        if DTGESN < 0:
            DTGESN = 0.0

        # File crop.go rows lines 644-649: calculation of WUMM
        WUMM = 0  # WUMM=N contained in dead roots, calculated as dead root biomass * concentr of N in roots
        # if root dry matter < root dry matter of previous day
        if g.WUMAS < g.WUMALT:
            WUMM = (g.WUMALT - g.WUMAS) * g.WUGEH
        else:
            WUMM = 0

        # cumulated N in dead roots
        g.CUMULATED_WUMM += WUMM

        # File crop.go rows lines 650-659: calculation of WURM: max root depth in dm

        # Calculation of root length density (root length density/cm^3 soil) -----
        WURM = int(math.floor((g.WURZMAX) * (
                    g.WUMAXPF / g.WUMAXPF)))  # davide: check this istruction. In the original code there is a /10. What does it mean?

        # condition not so good! in the hermes code the layers have all 10cm depth!
        # here it is not like this. TODO: We should add a better condition
        # if WURM > g.N :
        #    WURM = g.N

        if WURM > status.hermesnitrogen.MAXSOILDEPTH:
            WURM = status.hermesnitrogen.MAXSOILDEPTH

        if WURM < 1:
            WURM = 1

        # File crop.go rows lines 660-679: calculation of Qrez
        # QREZ represents the reciprocal value of the depth above which 63% of the roots are located. It is a variable in the exponential distribution of roots over depth
        velocity = 0
        tsumbase = 0
        if g.FRUCHT == "ORF" or g.FRUCHT == "ORH" or g.FRUCHT == "WRA" or g.FRUCHT == "ZR ":
            velocity = .004  # increase rooting depth (mm/C) = 0.8 =>  velocity = 0.8/200 = 0.004
            tsumbase = 185.
        else:
            if g.FRUCHT == "SM " or g.FRUCHT == "K  ":  # maize
                velocity = .0030  # increase rooting depth (mm/C) = 0.6 =>  velocity = 0.6/200 = 0.003  (value 0.6 for maize indicated by keserbaum)
                tsumbase = 211.
            else:  # winter wheat
                velocity = .002787  # increase rooting depth (mm/C) = 0.5574 =>  velocity = 0.5574/200 = 0.002787
                tsumbase = 265.
        Qrez = self.calculateQREZ(velocity, g.PHYLLO + g.TSUMEM, tsumbase)

        #old implementation
        # if g.FRUCHT == "ORF" or g.FRUCHT == "ORH" or g.FRUCHT == "WRA" or g.FRUCHT == "ZR ":
        #     Qrez = math.pow((0.081476 + math.exp(-.004 * (g.PHYLLO + g.TSUMEM + 185.))), 1.8)
        # else:
        #     if g.FRUCHT == "SM " or g.FRUCHT == "K  ":
        #         Qrez = math.pow((0.081476 + math.exp(-.0035 * (g.PHYLLO + g.TSUMEM + 211.))), 1.8)
        #     else:
        #         if g.FRUCHT == "GR " and g.AKF.Num > 2:
        #             Qrez = math.pow((0.081476 + math.exp(-.002787 * (math.Max(g.PHYLLO + g.TSUMEM, 1500)))), 1.8)
        #         else:
        #             if g.FRUCHT == "AA " and g.AKF.Num > 2:
        #                 Qrez = math.pow((0.081476 + math.exp(-.002787 * (math.Max(g.PHYLLO + g.TSUMEM, 1500)))), 1.8)
        #             else:
        #                 if g.FRUCHT == "CLU" and g.AKF.Num > 2:
        #                     Qrez = math.pow((0.081476 + math.exp(-.002787 * (math.Max(g.PHYLLO + g.TSUMEM, 1500)))),
        #                                     1.8)
        #                 else:
        #                     Qrez = math.pow((0.081476 + math.exp(-.002787 * (g.PHYLLO + g.TSUMEM + 265.))), 1.8)

        if Qrez > .35:
            Qrez = .35

        if Qrez < 4.5 / (WURM * DZ):  # DZ=10 is the thickness of every layer. TODO: modify this hardcoded behaviour!!
            Qrez = 4.5 / (WURM * DZ)

        # File crop.go rows lines 680-688: calculation of WRAD (root radius) for every soil level
        g.rootdepth_hermes = 4.5 / Qrez
        g.WURZ = int(4.5 / (Qrez * DZ))  # DZ is the thickness of every layer. TODO: modify this hardcoded behaviour!!
        # Assumption: root radius decrease with depth
        for i in range(1, g.WURZ + 1):
            if g.FRUCHT == "ZR " or g.FRUCHT == "K  ":
                status.hermesnitrogen.WRAD[i - 1] = .01
            else:
                status.hermesnitrogen.WRAD[i - 1] = .02 - i * 0.001

        # File crop.go rows lines 689-713: calculation of WULAE (root length), WUDICH (root length density) and FL (root surface) for every soil level
        for i in range(1, g.WURZ + 1):
            index = i - 1
            Tiefe = i * DZ
            status.hermesnitrogen.WULAE[index] = (g.WUMAS * (1 - math.exp(-Qrez * Tiefe)) / 100000 * 100 / 7)
            if i > 1:
                status.hermesnitrogen.WULAE2[index] = abs(
                    status.hermesnitrogen.WULAE[index] - status.hermesnitrogen.WULAE[index - 1]) / (
                                                                  math.pow(status.hermesnitrogen.WRAD[index],
                                                                           2) * math.pi) / DZ
            else:
                status.hermesnitrogen.WULAE2[index] = abs(status.hermesnitrogen.WULAE[index]) / (
                            math.pow(status.hermesnitrogen.WRAD[index], 2) * math.pi) / DZ

            # Wulae(i) = root length from layer 0 to depth I
            # -------------------------------------------------------------
            # ------ root length density/volume of soil -(cm/cm^3) ---------------
            # -------------------------------------------------------------
            status.hermesnitrogen.WUDICH[index] = status.hermesnitrogen.WULAE2[index]
            # ------------------------------------------------------------
            # ---------- root surface / dzmitt(i) * cm^3 Boden ----------
            # ------------------------------------------------------------
            status.hermesnitrogen.FL[index] = g.WUDICH[index] * status.hermesnitrogen.WRAD[index] * 2 * math.pi

        status.hermesnitrogen.WULAEN = 0
        for i in range(0, g.WURZ):
            # ---------------  root length in cm/cm^2 -----------------------
            status.hermesnitrogen.WULAEN = status.hermesnitrogen.WULAEN + status.hermesnitrogen.WULAE2[i] * DZ

        # File crop.go rows lines 714-717: calculation of N pools (NFOS= fast pool and NAOS = slow pool)
        for i in range(0,
                       3):  # WUMM = N contained in dead roots is ditributed in NFOS/NAOS in the first 3 layers. Each one gets 1/6 of it
            status.hermesmineralization.NFOS[i] = status.hermesmineralization.NFOS[i] + 0.5 * WUMM / 3
            status.hermesmineralization.NAOS[i] = status.hermesmineralization.NAOS[i] + 0.5 * WUMM / 3

        # File crop.go rows lines 718-733:  Limitation of maximum N-uptake to 26-13*10^-14 mol/cm W./sec   ( the number depends on the crop and on PHYLLO = cumulative development effective temperature sum (°C days) )
        # Limitation of maximum N-uptake to 26-13*10^-14 mol/cm W./sec
        maxup = 0
        if g.FRUCHT == "ORH" or g.FRUCHT == "WRA" or g.FRUCHT == "SE ":
            maxup = .09145 - .015725 * (g.PHYLLO / 1300)
        else:
            if g.FRUCHT == "SM ":
                maxup = .074 - .01 * (g.PHYLLO / g.tendsum)
            else:
                if g.FRUCHT == "ZR ":
                    maxup = .05645 - .01 * (g.PHYLLO / g.tendsum)
                else:
                    maxup = .03145 - .015725 * (g.PHYLLO / 1300)

        if DTGESN > status.hermesnitrogen.WULAEN * maxup:
            # if g.LEGUM != 'L':
            DTGESN = status.hermesnitrogen.WULAEN * maxup

        # File crop.go rows lines 734-745: calculation of N balance in the soil layers
        status.hermesnitrogen.NMINSUM = 0
        status.hermesnitrogen.TRNSUM = 0
        status.hermesnitrogen.SUMDIFF = 0
        # Calculation of maximum diffusive transport from Hermes. DIFF(I) =maximum diffusive transport layer I
        D = np.zeros(21, dtype=float)
        minim = min(g.WURZ, g.GRW)
        for index in range(0, minim):
            if index + 1 < 11:
                status.hermesnitrogen.NMINSUM = status.hermesnitrogen.NMINSUM + (status.hermestransport.C1[index] - .75)
                status.hermesnitrogen.MASS[index] = g.TP[index] * (status.hermestransport.C1[index] / (
                            g.WG[index] * DZ))  # TP[z] =water uptake in layer Z (SoilDepthLayer)
                status.hermesnitrogen.TRNSUM = status.hermesnitrogen.TRNSUM + g.TP[index] * (
                            status.hermestransport.C1[index] / (g.WG[index] * DZ))
                D[index] = 2.14 * (status.hermesnitrogen.params.AD * math.exp(g.WG[index] * 10)) / g.WG[index]
                status.hermesnitrogen.DIFF[index] = (D[index] * g.WG[index] * 2 * math.pi * status.hermesnitrogen.WRAD[
                    index]
                                                     * (status.hermestransport.C1[index] / 1000 / g.WG[
                            index] - .000014) * math.sqrt(math.pi * g.WUDICH[index])) \
                                                    * g.WUDICH[index] * 1000
                status.hermesnitrogen.SUMDIFF = status.hermesnitrogen.SUMDIFF + status.hermesnitrogen.DIFF[index]

        # File crop.go rows lines 750-775: calculation of SUMPE = sum of PE (N-uptake) for every layer
        status.hermesnitrogen.SUMPE = 0
        minim = min(g.WURZ, g.GRW)  # GRW=depth of ground water
        for index in range(0, minim):
            if DTGESN > 0:
                if status.hermesnitrogen.TRNSUM >= DTGESN:
                    status.hermesnitrogen.PE[index] = DTGESN * status.hermesnitrogen.MASS[
                        index] / status.hermesnitrogen.TRNSUM
                else:
                    if DTGESN - status.hermesnitrogen.TRNSUM < status.hermesnitrogen.SUMDIFF:
                        status.hermesnitrogen.PE[index] = status.hermesnitrogen.MASS[index] + (
                                    DTGESN - status.hermesnitrogen.TRNSUM) \
                                                          * status.hermesnitrogen.DIFF[
                                                              index] / status.hermesnitrogen.SUMDIFF
                    else:
                        status.hermesnitrogen.PE[index] = status.hermesnitrogen.MASS[index] + \
                                                          status.hermesnitrogen.DIFF[index]

                g.MASSUM = g.MASSUM + status.hermesnitrogen.MASS[index]
                g.DIFFSUM = g.DIFFSUM + status.hermesnitrogen.DIFF[index]
                if g.PE[index] > status.hermestransport.C1[index] - .75:
                    g.PE[index] = status.hermestransport.C1[index] - .75

                if g.PE[index] < 0:
                    g.PE[index] = 0

            else:
                g.PE[index] = 0

            status.hermesnitrogen.SUMPE = status.hermesnitrogen.SUMPE + g.PE[index]

        # File crop.go rows lines 776-786: calculation of NFIX (N fixation) for legumes (0 for other crops)
        NFIX = 0
        # TODO: for now we skip it

        # File crop.go rows lines 787-801: calculation of WUGEH (=N-content in root biomass)
        # if root dry matter > root dry matter of previous day
        if g.WUMAS > g.WUMALT:
            if g.FRUCHT == "ZR " or g.FRUCHT == "K  ":
                if (g.OBMAS - g.OBALT + g.WUMAS - g.WUMALT) > 0:
                    g.WUGEH = (g.WUMALT * g.WUGEH + ((g.WUMAS - g.WUMALT) / (g.OBMAS + g.WORG[
                        3] - g.OBALT + g.WUMAS - g.WUMALT) * status.hermesnitrogen.SUMPE)) / g.WUMAS

            else:
                if (g.OBMAS - g.OBALT + g.WUMAS - g.WUMALT) > 0:
                    g.WUGEH = (g.WUMALT * g.WUGEH + (g.WUMAS - g.WUMALT) / (g.OBMAS - g.OBALT + g.WUMAS - g.WUMALT) * (
                                status.hermesnitrogen.SUMPE + NFIX)) / g.WUMAS

            g.WUGEH = min(g.WUGEH, g.WGMAX)
            if g.WUGEH < 0.005:
                g.WUGEH = 0.005

        # File crop.go rows lines 802-810:calculation of WUGEH (=N-content in roots ) and GEHOB (=N-content in above ground biomass )
        if g.FRUCHT == "ZR " or g.FRUCHT == "K  ":
            g.GEHOB = (g.PESUM + status.hermesnitrogen.SUMPE - g.WUMAS * g.WUGEH) / (g.OBMAS + g.WORG[3])
            if g.GEHOB * (g.OBMAS + g.WORG[3]) < g.OBALT * g.GEHALT:
                g.WUGEH = (g.PESUM + status.hermesnitrogen.SUMPE - (g.OBMAS + g.WORG[3]) * g.GEHOB) / (g.WUMAS)
        else:
            g.GEHOB = (g.PESUM + status.hermesnitrogen.SUMPE + NFIX - g.WUMAS * g.WUGEH) / g.OBMAS

        g.N_IN_WU = g.WUMAS * g.WUGEH

        return status

    def integrate(self, status):
        return status
