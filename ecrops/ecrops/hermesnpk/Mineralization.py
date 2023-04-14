# -*- coding: utf-8 -*-
#
# This component was derived from Hermes model (by professor Kurt Christian Kersebaum (Leibniz Centre for Agricultural Landscape Research)) and traslated and adapted by JRC for the eCrops framework
# European Commission, Joint Research Centre, March 2023


import numpy as np

from ..Printable import Printable
import math


class Mineralization:
    """Mineralisation from Hermes. Copied from file nitro.go, rows 449-550"""

    # Mineralisation depending on temperature and water content ------------
    # Inputs:
    # IZM                       = soil specific depth for mineralisation (sand > clay)
    # TEMP(TAG)                 = daily mean temperature at day TAG (°C)
    # TSOIL(0,Z)                = Soil temperature at begin time step in layer Z  (°C)
    # WG(0,Z)                   = Water content at begin time step in layer Z  (cm^3/cm^3)
    # WNOR(Z)                   = NORM-field capacity (without water logging) in layer Z (cm^3/cm^3)
    # WMIN(Z)                   = Water content at wilting point in layer Z (cm^3/cm^3)
    # PORGES(Z)                 = Total pore space in layer Z  (cm^3/cm^3)
    # MINAOS(Z)                 = already mineralized N of pool NAOS (slow pool) in Z (kg N/ha)
    # MINFOS(Z)                 = already mineralized N of pool NFOS (fast pool) in Z (kg N/ha)
    # DSUMM                     = Summe of applied mineral N (kg N/ha)
    # UMS                       = Summe of mineral N in soil solution N (kg N/ha)

    # W                         =FIELD CAPACITY (cm^3/cm^3) ?? which is the difference from  WNOR ???

    def getparameterslist(self):
        return {
        }

    def setparameters(self, status):


        return status

    def initialize(self, status):
        # initialize outputs
        status.hermesmineralization.MIRED = np.zeros(( 21),
                                                     dtype=float)  # reduction factor when water is sub optimal (Myers) in layer Z
        status.hermesmineralization.MINAOS = np.zeros(( 21),
                                                      dtype=float)  # already mineralized N of pool NAOS (slow pool) in Z (kg N/ha)#todo:hardcoded!
        status.hermesmineralization.MINFOS = np.zeros(( 21),
                                                      dtype=float)  # already mineralized N of pool NFOS (fast pool) in Z (kg N/ha) #todo:hardcoded!
        status.hermesmineralization.DTOTALN = np.zeros(( 21),
                                                       dtype=float)  # Mineralisation during time step of pool NAOS (slow pool) in Z
        status.hermesmineralization.DMINFOS = np.zeros(( 21),
                                                       dtype=float)  # Mineralisation during time step of pool NFOS (fast pool) in Z
        status.hermesmineralization.DUMS = np.zeros(( 21),
                                                    dtype=float)  # olution of remained solid mineral fertilizer during time step  ( >0 only for the first soil layer)



        status.hermesmineralization.DSUMM = 0 # Summe of applied mineral N (kg N/ha)
        status.hermesmineralization.UMS = 0  # Sum of mineral N in soil solution N (kg N/ha)
        status.hermesmineralization.MINSUM = 0  # total mineralization (sums of UMS in all the layers)
        status.hermesmineralization.DN = np.zeros(( 21), dtype=float)  # sum of all transfers
        status.hermesmineralization.IZM=30 #IZM= soil specific depth for mineralisation (sand > clay) in cm //TODO hardocoded for now
        status.hermesmineralization.DZ=10  # DZ= soil layer depth




        return status

    def runstep(self, status):
        g = status.hermesmineralization


        # Soil temperature #TODO for now set to tmin for every layer
        status.hermesmineralization.TD = status.weather.TEMP_MIN * np.ones((21),  dtype=float)

        num = math.floor(g.IZM / g.DZ)  # DZ = layer depth
        for z in range(1, num + 1):
            zIndex = z - 1
            # averaging soil temperature for layer z from upper and lower boundary depth
            TEMPBO = (g.TD[z] + g.TD[z - 1]) / 2
            # --------- calculation of mineralisation coefficient ---------
            # ----------- depending on temperature and water -----------
            # - solution of solid mineral N to soil solution
            KTD = .4
            # no mineralisation when temperature <= 0
            if TEMPBO > 0:
                # mineralisation coefficient of slowly decpomposable fraction NAOS
                kt0 = 4000000000. * math.exp(-8400. / (TEMPBO + 273.16))
                # mineralisation coefficient of fast decpomposable fraction NFOS
                kt1 = 5.6e+12 * math.exp(-9800. / (TEMPBO + 273.16))


                # calculation of MIRED=reduction factor when water is sub optimal
                if g.WG[zIndex] <= g.WNOR[zIndex] and g.WG[zIndex] >= g.WRED:
                    status.hermesmineralization.MIRED[zIndex] = 1
                else:
                    if g.WG[zIndex] < g.WRED and g.WG[zIndex] > g.WMIN[zIndex]:
                        status.hermesmineralization.MIRED[zIndex] = (g.WG[zIndex] - g.WMIN[zIndex]) / (
                                    g.WRED - g.WMIN[zIndex])
                    else:
                        if g.WG[zIndex] > g.WNOR[zIndex]:
                            status.hermesmineralization.MIRED[zIndex] = (g.PORGES[zIndex] - g.WG[zIndex]) / (
                                        g.PORGES[zIndex] - g.WNOR[zIndex])
                        else:
                            status.hermesmineralization.MIRED[zIndex] = 0

                if status.hermesmineralization.MIRED[zIndex] < 0:
                    status.hermesmineralization.MIRED[zIndex] = 0

                if status.hermesmineralization.MIRED[zIndex] > 1:
                    status.hermesmineralization.MIRED[zIndex] = 1

                # Mineralisation during time step of the slowly decomposable organic fraction
                status.hermesmineralization.DTOTALN[zIndex] = kt0 * g.NAOS[zIndex] * status.hermesmineralization.MIRED[
                    zIndex]

                if status.hermesmineralization.DTOTALN[zIndex] < 0:
                    status.hermesmineralization.DTOTALN[zIndex] = 0

                g.NAOS[zIndex] = g.NAOS[zIndex] - status.hermesmineralization.DTOTALN[zIndex]
                # Mineralisation during time step of the fast decomposable organic fraction
                status.hermesmineralization.DMINFOS[zIndex] = kt1 * g.NFOS[zIndex] * status.hermesmineralization.MIRED[
                    zIndex]
                if status.hermesmineralization.DMINFOS[zIndex] < 0:
                    status.hermesmineralization.DMINFOS[zIndex] = 0

                g.NFOS[zIndex] = g.NFOS[zIndex] - status.hermesmineralization.DMINFOS[zIndex]
                # solution of remained solid mineral fertilizer during time step
                if z == 1:
                    g.DUMS[zIndex] = KTD * status.hermesmineralization.MIRED[zIndex] * (g.DSUMM - g.UMS)
                else:
                    g.DUMS[zIndex] = 0

                # sum of all transfers => source term ( dn(z) )
                g.DN[zIndex] = status.hermesmineralization.DTOTALN[zIndex] + status.hermesmineralization.DMINFOS[
                    zIndex] + g.DUMS[zIndex]
                # --- summation of all pools transfers -----
                g.MINAOS[zIndex] = g.MINAOS[zIndex] + status.hermesmineralization.DTOTALN[zIndex]
                g.MINFOS[zIndex] = g.MINFOS[zIndex] + status.hermesmineralization.DMINFOS[zIndex]
                g.UMS = g.UMS + g.DUMS[zIndex]
                g.MINSUM = g.MINSUM + g.DN[zIndex] - g.DUMS[zIndex]
                # -- at temperature below zero only solution of mineral fertilizer depending on water ---
            else:
                if z == 1:
                    # Reduction factor when water is sub optimal
                    if g.WG[zIndex] < g.W[zIndex] and g.WG[zIndex] > g.WRED:
                        status.hermesmineralization.MIRED[zIndex] = 1
                    else:
                        if g.WG[zIndex] < g.WRED:
                            status.hermesmineralization.MIRED[zIndex] = (g.WG[zIndex] - g.WMIN[zIndex]) / (
                                        g.WRED - g.WMIN[zIndex])
                        else:
                            if g.WG[zIndex] > g.W[zIndex] + .01 and g.WG[zIndex] < g.PORGES[0]:
                                status.hermesmineralization.MIRED[zIndex] = (g.PORGES[0] - g.WG[zIndex]) / (
                                            g.PORGES[0] - g.W[zIndex])
                            else:
                                if g.WG[zIndex] > g.PORGES[0]:
                                    status.hermesmineralization.MIRED[zIndex] = 0
                                else:
                                    status.hermesmineralization.MIRED[zIndex] = 1

                    if status.hermesmineralization.MIRED[zIndex] < 0:
                        status.hermesmineralization.MIRED[zIndex] = 0

                    g.DUMS[zIndex] = .4 * status.hermesmineralization.MIRED[zIndex] * (g.DSUMM - g.UMS)
                else:
                    g.DUMS[zIndex] = 0

                g.UMS = g.UMS + g.DUMS[zIndex]
                g.DN[zIndex] = g.DUMS[zIndex]

        return status

    def integrate(self, status):
        return status
