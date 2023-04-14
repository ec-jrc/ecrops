# -*- coding: utf-8 -*-
#
# This component was derived from Hermes model (by professor Kurt Christian Kersebaum (Leibniz Centre for Agricultural Landscape Research)) and traslated and adapted by JRC for the eCrops framework
# European Commission, Joint Research Centre, March 2023


import numpy as np

from ..Printable import Printable
import math


class Denitrification:
    """Denitrification from Hermes. Copied from file denit.go , rows 1-50"""

    #   /*  Denitrification sub model                                    */
    #   /*  acc. U. Schneider, Diss. 1991, und Richter & Soendgerat        */
    #   /*  Jan. 1992                                                     */
    # Inputs:
    # WG(1,I) 		= water content layer I (cm^3/cm^3)
    # PORGES(I)		= Total pore space (cm^3/cm^3)
    # C1(I)		= soil mineral N (NO3) layer I (kg N/ha)
    # Tsoil(0,I)	= Soil temperature in layer I (°C)

    def getparameterslist(self):
        return {
        }

    def setparameters(self, status):

        return status

    def initialize(self, status):

        status.hermesmineralization.subd = 1  # number of subdivisions in a day
        status.hermesmineralization.wdt = 1  # fraction of day ( the time step of one day is sometimes reduced when water flux becommes too high)
        status.hermesmineralization.CUMDENIT = 0
        status.hermesmineralization.thetasatFromPorges = False  # TODO:??? true o false ???

        # initialize outputs

        return status

    def runstep(self, status):
        g = status.hermesmineralization

        # Soil temperature #TODO for now set to tmin for every layer
        status.hermesmineralization.TSOIL = status.weather.TEMP_MIN * np.ones((21), dtype=float)

        thetaOb30 = (g.WG[0] + g.WG[1] + g.WG[2]) / 3
        thetasat = 0
        if status.hermesmineralization.thetasatFromPorges:
            thetasat = (g.PORGES[0] + g.PORGES[1] + g.PORGES[2]) / 3
        else:
            thetasat = 1 - (1.45 / 2.65)

        thetarel = thetaOb30 / thetasat
        nitratOb30 = status.hermestransport.C1[0] + status.hermestransport.C1[1] + status.hermestransport.C1[2]
        tempOb30 = (g.TSOIL[0] + g.TSOIL[1] + g.TSOIL[2] + g.TSOIL[3]) / 4
        if tempOb30 < 0:
            tempOb30 = 0

        #
        #   /*  Parameter from U. Schneider, Diss. '91. S.57, 0-30 cm        */
        #   /*  Vmax   =  1274    (g/ha/day)                                  */
        #   /*  KNO3   =  74      (kg/ha/30 cm depth)                         */
        #   /*  Tkrt   =  15.5    (degrees Celsius)                           */
        #   /*  Okrt   =  0.766   (relative volumetric water content)      */
        Vmax = 1274.
        KNO3 = 74.
        Tkrt = 15.5
        Okrt = 0.766
        Nquadrat = math.pow(nitratOb30, 2)
        michment = (Vmax * Nquadrat) / (Nquadrat + KNO3)
        Ftheta = 1 - math.exp(-1 * math.pow((thetarel / Okrt), 6))
        Ftemp = 1 - math.exp(-1 * math.pow((tempOb30 / Tkrt), 4.6))
        DENIT = michment * Ftheta * Ftemp
        DENIT = DENIT / 1000
        #   /* Denitrification N is substracted from NO3 pool                    */
        status.hermestransport.C1[0] = status.hermestransport.C1[0] - DENIT / 3
        status.hermestransport.C1[1] = status.hermestransport.C1[1] - DENIT / 3
        status.hermestransport.C1[2] = status.hermestransport.C1[2] - DENIT / 3
        g.CUMDENIT = g.CUMDENIT + DENIT

        # N balance calculation
        # total N in system = denitrification + leaching + pesum + N in C1 + N in pools - N in dead roots
        status.hermestransport.totNinC1_rootable = 0
        status.hermestransport.totNinC1_unrootable = 0
        status.hermestransport.totNinpools_rootable = 0
        status.hermestransport.totNinpools_unrootable = 0
        for z in range(0, status.hermestransport.N):
            if z < status.hermestransport.OUTN :
                status.hermestransport.totNinC1_rootable += status.hermestransport.C1[z]
                status.hermestransport.totNinpools_rootable += status.hermesmineralization.NFOS[z] + \
                                                               status.hermesmineralization.NAOS[z]
            else:
                status.hermestransport.totNinC1_unrootable += status.hermestransport.C1[z]
                status.hermestransport.totNinpools_unrootable += status.hermesmineralization.NFOS[z] + \
                                                               status.hermesmineralization.NAOS[z]

        status.hermestransport.TotalNInSystem = status.hermesmineralization.CUMDENIT + status.hermestransport.OUTSUM + status.hermesnitrogen.PESUM + status.hermestransport.totNinC1_rootable + status.hermestransport.totNinpools_rootable -status.hermesnitrogen.CUMULATED_WUMM

        return status

    def integrate(self, status):


        return status
