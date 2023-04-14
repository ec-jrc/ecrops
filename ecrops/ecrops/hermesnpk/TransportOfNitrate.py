# -*- coding: utf-8 -*-
#
# This component was derived from Hermes model (by professor Kurt Christian Kersebaum (Leibniz Centre for Agricultural Landscape Research)) and traslated and adapted by JRC for the eCrops framework
# European Commission, Joint Research Centre, March 2023



import numpy as np

from ..Printable import Printable
import math


class TransportOfNitrate:
    """Transport of Nitrate from Hermes. Copied from file nitro.go, rows 554-686
    
    Inputs:
    -DV                        = Dispersion length for convection-dispersion equation (cm)
    -FLUSS                    = Infiltration through soil surface (cm/d)
    -Q1(Z)                     = Water flux through lower boundary of layer z (cm/d)
    -QDRAIN                    = Water flux to tile drain (cm/d)
    -DRAIDEP                   = depth of tile drain (dm)
    -AD                        = Faktor for diffusivity
    -DZ                        = Thickness layer (cm)
    -WG(0,Z)                   = Water content at begin time step in layer Z  (cm^3/cm^3)
    -WNOR(Z)                   = NORM-field capacity (without water logging) in layer Z (cm^3/cm^3)
    -WMIN(Z)                   = Water content at wilting point in layer Z (cm^3/cm^3)
    -PORGES(Z)                 = Total pore space in layer Z  (cm^3/cm^3)
    -PE(Z)                     = N-uptake of crop in layer Z (kg N/ha)
    -C1(Z)                     = Soil mineral N content (NO3+NH4) in layer Z (kg N/ha)
    -DN(Z)                     = Source term from mineralisation routine (kg N/ha) in layer Z
    -OUTN                      = Depth for seepage and N-leaching (to be defined by user) (dm)
    -W                            = FIELD CAPACITY (cm^3/cm^3)
    
    """


    def getparameterslist(self):
        return {
        }

    def setparameters(self, status):
        return status

    def initialize(self, status):

        status.hermestransport.subd = 1  # number of subdivisions in a day
        status.hermestransport.wdt = 1  # fraction of day ( the time step of one day is sometimes reduced when water flux becommes too high)

        # initialize outputs
        status.hermestransport.D = np.zeros((21), dtype=float)
        status.hermestransport.V = np.zeros((21), dtype=float)
        status.hermestransport.DB = np.zeros((21), dtype=float)
        status.hermestransport.DISP = np.zeros((21), dtype=float)
        status.hermestransport.KONV = np.zeros((21), dtype=float)

        status.hermestransport.DZ = 10

        status.hermestransport.FLUSS0 = 0

        status.hermestransport.DV = 1  # TODO: which value?
        status.hermestransport.DRAIDEP = 10  # depth of tile drain (dm). TODO: now fized to 1m depth
        status.hermestransport.DRAINLOSS = 0
        status.hermestransport.QDRAIN = 0
        status.hermestransport.OUTSUM = 0
        status.hermestransport.AUFNASUM = 0
        status.hermestransport.NLEAG = 0
        status.hermestransport.C1stabilityVal = 0
        status.hermestransport.SCHNORR = 0  # amount of fixed nitrogen for legumes

        return status

    def runstep(self, status):
        g = status.hermestransport

        zeit = status.doy

        Carray = np.zeros(21, dtype=float)
        for z in range(0, g.N):
            # --- Calculation of diffusion coefficient at lower boundary of layer Z ( diffusion coeff. of NO3 in water 2.14 cm^2 day^-1)---
            g.D[z] = 2.14 * (status.hermestransport.params.AD * math.exp((g.WG[z] + g.WG[z + 1]) * 5) / (
                    (g.WG[z] + g.WG[z + 1]) / 2)) * status.hermestransport.wdt
            if status.hermestransport.subd == 1:
                if status.hermesnitrogen.PE[z] > g.C1[z] - .5:
                    status.hermesnitrogen.PE[z] = (g.C1[z] - .5)

                if status.hermesnitrogen.PE[z] < 0:
                    status.hermesnitrogen.PE[z] = 0

                status.hermesnitrogen.PESUM = status.hermesnitrogen.PESUM + status.hermesnitrogen.PE[z]
                g.AUFNASUM = g.AUFNASUM + status.hermesnitrogen.PE[z]
                g.C1[z] = g.C1[z] - status.hermesnitrogen.PE[z]

            Carray[z + 1] = (g.C1[z] + status.hermesmineralization.DN[z] * status.hermestransport.wdt / 2) / (
                    g.WG[z] * g.DZ * 100)

        # --------------------- downward movement ---------------------
        g.Q1[0] = g.FLUSS0 * status.hermestransport.wdt
        for zIndex0 in range(0, g.N):
            zIndex1 = zIndex0 + 1
            # Pore water velocity V
            g.V[zIndex0] = abs(g.Q1[zIndex1] / ((g.W[zIndex0] + g.W[zIndex0 + 1]) * .5))
            # ---- diffusion dispersion part of convection-dispersion equation (only one-dicectional at upper and lower boundary)----
            g.DB[zIndex0] = (g.WG[zIndex0] + g.WG[zIndex0 + 1]) / 2 * (
                    g.D[zIndex0] + g.DV * g.V[zIndex0]) - 0.5 * status.hermestransport.wdt * abs(
                g.Q1[zIndex1]) + 0.5 * status.hermestransport.wdt * abs((g.Q1[zIndex1] + g.Q1[zIndex1 - 1]) / 2) * \
                            g.V[zIndex0]
            if zIndex1 == 1:
                cVar = Carray[zIndex1] - Carray[zIndex1 + 1]
                dbVar = -g.DB[zIndex0]
                num100 = math.pow(g.DZ, 2)
                g.DISP[zIndex0] = dbVar * cVar / num100
            else:
                if zIndex1 < g.N:
                    g.DISP[zIndex0] = g.DB[zIndex0 - 1] * (Carray[zIndex1 - 1] - Carray[zIndex1]) / math.pow(g.DZ,
                                                                                                             2) - g.DB[
                                          zIndex0] * (Carray[zIndex1] - Carray[zIndex1 + 1]) / math.pow(g.DZ, 2)
                else:
                    g.DISP[zIndex0] = g.DB[zIndex0 - 1] * (Carray[zIndex1 - 1] - Carray[zIndex1]) / math.pow(g.DZ,
                                                                                                             2)

        #  --- konvective part of convection-dispersion equation
        for z in range(1, g.N + 1):
            z0 = z - 1
            # -- flow at top and bottom of layer z downward (positive)
            if g.Q1[z] >= 0 and g.Q1[z - 1] >= 0:
                if z == g.DRAIDEP:
                    g.KONV[z0] = (Carray[z] * g.Q1[z] + Carray[z] * g.QDRAIN - Carray[z - 1] * g.Q1[z - 1]) / g.DZ
                else:
                    g.KONV[z0] = (Carray[z] * g.Q1[z] - Carray[z - 1] * g.Q1[z - 1]) / g.DZ

            # -- flow at top negative and positive at bottom of layer z (depletion)
            else:
                if g.Q1[z] >= 0 and g.Q1[z - 1] < 0:
                    if z > 1:
                        if z == g.DRAIDEP:
                            g.KONV[z0] = (Carray[z] * g.Q1[z] + Carray[z] * g.QDRAIN - Carray[z] * g.Q1[
                                z - 1]) / g.DZ
                        else:
                            g.KONV[z0] = (Carray[z] * g.Q1[z] - Carray[z] * g.Q1[z - 1]) / g.DZ

                    else:
                        g.KONV[z0] = Carray[z] * g.Q1[z] / g.DZ

                # -- flow at top and bottom of layer z upward (negative)
                else:
                    if g.Q1[z] < 0 and g.Q1[z - 1] < 0:
                        if z > 1:
                            g.KONV[z0] = (Carray[z + 1] * g.Q1[z] - Carray[z] * g.Q1[z - 1]) / g.DZ
                        else:
                            g.KONV[z0] = Carray[z + 1] * g.Q1[z] / g.DZ

                    # flow at top positive and bottom of layer z negative (accumulation)
                    else:
                        if g.Q1[z] < 0 and g.Q1[z - 1] >= 0:
                            g.KONV[z0] = (Carray[z + 1] * g.Q1[z] - Carray[z - 1] * g.Q1[z - 1]) / g.DZ

        # -- summing loss to tile drain --
        g.DRAINLOSS = g.DRAINLOSS + g.QDRAIN * Carray[g.DRAIDEP] / g.DZ * 100 * g.DZ

        # combination of convection and dispersion
        for z in range(0, g.N):
            g.C1[z] = (Carray[z + 1] * g.WG[z] + g.DISP[z] - g.KONV[z]) * g.DZ * 100

        # ----------- sumation of flows for output ----------
        if g.Q1[g.OUTN] > 0:
            if g.OUTN < g.N:
                g.OUTSUM = g.OUTSUM + g.Q1[g.OUTN] * Carray[g.OUTN] / g.DZ * 100 * g.DZ + g.DB[g.OUTN - 1] * (
                        Carray[g.OUTN] - Carray[g.OUTN + 1]) / math.pow(g.DZ, 2) * 100 * g.DZ
                if zeit > g.SAAT:
                    g.NLEAG = g.NLEAG + g.Q1[g.OUTN] * Carray[g.OUTN] / g.DZ * 100 * g.DZ + g.DB[g.OUTN - 1] * (
                            Carray[g.OUTN] - Carray[g.OUTN + 1]) / math.pow(g.DZ, 2) * 100 * g.DZ

            else:
                g.OUTSUM = g.OUTSUM + g.Q1[g.OUTN] * Carray[g.OUTN] / g.DZ * 100 * g.DZ
                if zeit > g.SAAT:
                    g.NLEAG = g.NLEAG + g.Q1[g.OUTN] * Carray[g.OUTN] / g.DZ * 100 * g.DZ


        else:
            if g.OUTN < g.N:
                g.OUTSUM = g.OUTSUM + g.Q1[g.OUTN] * Carray[g.OUTN + 1] / g.DZ * 100 * g.DZ + g.DB[
                    g.OUTN - 1] * (Carray[g.OUTN] - Carray[g.OUTN + 1]) / math.pow(g.DZ, 2) * 100 * g.DZ
                if zeit > g.SAAT:
                    g.NLEAG = g.NLEAG + g.Q1[g.OUTN] * Carray[g.OUTN + 1] / g.DZ * 100 * g.DZ + g.DB[
                        g.OUTN - 1] * (Carray[g.OUTN] - Carray[g.OUTN + 1]) / math.pow(g.DZ, 2) * 100 * g.DZ

        g.C1NotStable = ""
        for z in range(0, g.N):
            g.C1[z] = g.C1[z] + status.hermesmineralization.DN[z] * status.hermestransport.wdt / 2

            # C1 may be below 0 because of rounding issues, set it to 0
            # if C1 is significat below zero, there might be an instabily in the calculations
            if g.C1[z] < g.C1stabilityVal:
                g.C1NotStable = "C1 unstable"
                g.C1NotStableErr = "C1 unstable"

            if g.C1[z] < 0:
                g.C1[z] = 0

        status.hermesnitrogen.PESUM = status.hermesnitrogen.PESUM + g.SCHNORR

        return status

    def integrate(self, status):
        return status
