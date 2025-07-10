# -*- coding: utf-8 -*-
# This component is derived from PCSE software 6.0 /Wofost model 8.1
# (Copyright @ 2004-2024 Alterra, Wageningen-UR; Allard de Wit allard.dewit@wur.nl, April 2024)
# and modified by EC-JRC for the eCrops framework under the European Union Public License (EUPL), Version 1.2
# European Commission, Joint Research Centre, March 2023




from __future__ import print_function

from math import log10, sqrt, exp, isnan

import numpy as np
from ecrops.Printable import Printable

from ecrops.wofost_util import Afgen
from ecrops.wofost_util.util import limit
from ecrops.Step import Step



# -------------------------------------------------------------------------------
class WaterbalanceLayered(Step):
    """This implements a layered water balance to estimate soil water availability for crop growth and water stress.

    The classic free-drainage water-balance had some important limitations such as the inability to take into
    account differences in soil texture throughout the profile and its impact on soil water flow. Moreover,
    in the single layer water balance, rainfall or irrigation will become immediately available to the crop.
    This is incorrect physical behaviour and in many situations it leads to a very quick recovery of the crop
    after rainfall since all the roots have immediate access to infiltrating water. Therefore, with more detailed
    soil data becoming available a more realistic soil water balance was deemed necessary to better simulate soil
    processes and its impact on crop growth.

    The multi-layer water balance represents a compromise between computational complexity, realistic simulation
    of water content and availability of data to calibrate such models. The model still runs on a daily time step
    but does implement the concept of downward and upward flow based on the concept of hydraulic head and soil
    water conductivity. The latter are combined in the so-called Matric Flux Potential. The model computes
    two types of flow of water in the soil:

      (1) a "dry flow" from the matric flux potentials (e.g. the suction gradient between layers)
      (2) a "wet flow" under the current layer conductivities and downward gravity.

    Clearly, only the dry flow may be negative (=upward). The dry flow accounts for the large
    gradient in water potential under dry conditions (but neglects gravity). The wet flow takes into
    account gravity only and will dominate under wet conditions. The maximum of the dry and wet
    flow is taken as the downward flow, which is then further limited in order the prevent
    (a) oversaturation and (b) water content to decrease below field capacity.
    Upward flow is just the dry flow when it is negative. In this case the flow is limited
    to a certain fraction of what is required to get the layers at equal potential, taking
    into account, however, the contribution of an upward flow from further down.

    The configuration of the soil layers is variable but is bound to certain limitations:

    - The layer thickness cannot be made too small. In practice, the top layer should not
      be smaller than 10 to 20 cm. Smaller layers would require smaller time steps than
      one day to simulate realistically, since rain storms will fill up the top layer very
      quickly leading to surface runoff because the model cannot handle the infiltration of
      the rainfall in a single timestep (a day).
    - The crop maximum rootable depth must coincide with a layer boundary. This is to avoid
      that roots can directly access water below the rooting depth. Of course such water may become
      available gradually by upward flow of moisture at some point during the simulation.

    The current python implementation does not yet implement the impact of shallow groundwater
    but this will be added in future versions of the model.

    For an introduction to the concept of Matric Flux Potential see for example:

        Pinheiro, Everton Alves Rodrigues, et al. “A Matric Flux Potential Approach to Assess Plant Water
        Availability in Two Climate Zones in Brazil.” Vadose Zone Journal, vol. 17, no. 1, Jan. 2018, pp. 1–10.
        https://doi.org/10.2136/vzj2016.09.0083.

    **Note**: the current implementation of the model (April 2024) is rather 'Fortran-ish'. This has been done
    on purpose to allow comparisons with the original code in Fortran90. When we are sure that
    the implementation performs properly, we can refactor this in to a more functional structure
    instead of the current code which is too long and full of loops.


    **Simulation parameters:**

    Besides the parameters in the table below, the multi-layer waterbalance requires
    a `SoilProfileDescription` which provides the properties of the different soil
    layers. See the `SoilProfile` and `SoilLayer` classes for the details.

    ========== ====================================================  ====================
     Name      Description                                           Unit
    ========== ====================================================  ====================
    NOTINF     Maximum fraction of rain not-infiltrating into          -
               the soil
    IFUNRN     Indicates whether non-infiltrating fraction of   SSi    -
               rain is a function of storm size (1)
               or not (0)
    SSI        Initial surface storage                                 cm
    SSMAX      Maximum surface storage                                 cm
    SMLIM      Maximum soil moisture content of top soil layer         cm3/cm3
    WAV        Initial amount of water in the soil                     cm
    ========== ====================================================  ====================


    **State variables:**

    =======  ========================================================  ============
     Name     Description                                                  Unit
    =======  ========================================================  ============
    WTRAT     Total water lost as transpiration as calculated           cm
              by the water balance. This can be different
              from the CTRAT variable which only counts
              transpiration for a crop cycle.
    EVST      Total evaporation from the soil surface                   cm
    EVWT      Total evaporation from a water surface                    cm
    TSR       Total surface runoff                                      cm
    RAINT     Total amount of rainfall (eff + non-eff)                  cm
    WDRT      Amount of water added to root zone by increase            cm
              of root growth
    TOTINF    Total amount of infiltration                              cm
    TOTIRR    Total amount of effective irrigation                      cm

    SM        Volumetric moisture content in the different soil          -
              layers (array)
    WC        Water content in the different soil                       cm
              layers (array)
    W         Amount of water in root zone                              cm
    WLOW      Amount of water in the subsoil (between current           cm
              rooting depth and maximum rootable depth)
    WWLOW     Total amount of water                                     cm
              in the  soil profile (WWLOW = WLOW + W)
    WBOT      Water below maximum rootable depth and unavailable
              for plant growth.                                         cm
    WAVUPP    Plant available water (above wilting point) in the        cm
              rooted zone.
    WAVLOW    Plant available water (above wilting point) in the        cm
              potential root zone (below current roots)
    WAVBOT    Plant available water (above wilting point) in the        cm
              zone below the maximum rootable depth
    SS        Surface storage (layer of water on surface)               cm
    SM_MEAN   Mean water content in rooted zone                         cm3/cm3
    PERCT     Total amount of water percolating from rooted             cm
              zone to subsoil
    LOSST     Total amount of water lost to deeper soil                 cm
    =======  ========================================================  ============


    **Rate variables**

    ========== ==================================================  ====================
     Name      Description                                          Unit
    ========== ==================================================  ====================
    Flow        Rate of flow from one layer to the next              cm/day
    RIN         Rate of infiltration at the surface                  cm/day
    WTRALY      Rate of transpiration from the different
                soil layers (array)                                  cm/day
    WTRA        Total crop transpiration rate accumulated over       cm/day
                soil layers.
    EVS         Soil evaporation rate                                cm/day
    EVW         Open water evaporation rate                          cm/day
    RIRR        Rate of irrigation                                   cm/day
    DWC         Net change in water amount per layer (array)         cm/day
    DRAINT      Change in rainfall accumlation                       cm/day
    DSS         Change in surface storage                            cm/day
    DTSR        Rate of surface runoff                               cm/day
    BOTTOMFLOW  Flow of the bottom of the profile                    cm/day
    ========== ==================================================  ====================

    """
    # INTERNALS
    RDold = float(-99.)  # previous maximum rooting depth value
    RDMSLB = float(-99.)  # max rooting depth soil layer boundary



    XDEF = 1000.0  # maximum depth of groundwater (in cm)
    PFFC = 2.0  # PF field capacity, Float(log10(200.))
    PFWP = log10(16000.)  # PF wilting point
    PFSAT = -1.0  # PF saturation

    EquilTableLEN = 30  # GW: WaterFromHeight, HeightFromAir


    # ------------------------------------------

    def getparameterslist(self):
        return {
            "RDI": {"Description": "Initial root depth", "Type": "Number", "Mandatory": "True", "UnitOfMeasure": "cm"},
            "RDMCR": {"Description": "Maximum root depth", "Type": "Number", "Mandatory": "True",
                      "UnitOfMeasure": "cm"},
            "IAIRDU": {"Description": "Switch airducts on (1) or off (0)", "Type": "Number", "Mandatory": "True",
                       "UnitOfMeasure": "unitless"},
            "CALC_SOILWATER_BEFORE_SOWING": {"Description": "Optional parameter for trtiggering the soil water calculation in advance", "Type": "Number", "Mandatory": "False",
                       "UnitOfMeasure": "unitless"},

        }

    def setparameters(self, status):

        status.layeredwaterbalance = Printable()
        status.layeredwaterbalance.states = Printable()
        status.layeredwaterbalance.rates = Printable()
        status.soildata = Printable()
        status.soildata = status.soilparameters
        status.layeredwaterbalance.parameters = Printable()
        status.layeredwaterbalance.parameters.RDI = status.allparameters["RDI"]
        status.layeredwaterbalance.parameters.IAIRDU = status.allparameters["IAIRDU"]
        status.layeredwaterbalance.parameters.RDMCR = status.allparameters["RDMCR"]
        status.layeredwaterbalance.parameters.GW = status.soildata['GW']
        status.layeredwaterbalance.parameters.ZTI = status.soildata['ZTI']
        status.layeredwaterbalance.parameters.DD = status.soildata['DD']
        status.layeredwaterbalance.parameters.NSL = status.soildata['NSL']
        status.layeredwaterbalance.parameters.IFUNRN = status.soildata['IFUNRN']
        status.layeredwaterbalance.parameters.SSMAX = status.soildata['SSMAX']
        status.layeredwaterbalance.parameters.SSI = status.soildata['SSI']
        status.layeredwaterbalance.parameters.NOTINF = status.soildata['NOTINF']
        status.layeredwaterbalance.parameters.SMLIM = status.soildata['SMLIM']
        status.layeredwaterbalance.parameters.SOIL_LAYERS = status.soildata['SOIL_LAYERS']
        status.layeredwaterbalance.parameters.RDMSOL = status.layeredwaterbalance.parameters.SOIL_LAYERS[-1].LBSL

        # Fraction of non-infiltrating rainfall as function of storm size
        status.layeredwaterbalance.parameters.NINFTB = Afgen.Afgen([0.0, 0.0, 0.5, 0.0, 1.5, 1.0, 0.0, 0.0, 0.0, 0.0, \
                                                                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                                                    0.0])  # hardcoded in the original version

        # read from the parameters the value of parameter CALC_SOILWATER_BEFORE_SOWING and set accordingly the booleans for soil water calculation in advance.
        #
        # CALC_SOILWATER_BEFORE_SOWING = 0: no soil moisture calculation in advance, no ISW.
        #
        # CALC_SOILWATER_BEFORE_SOWING = 1: the soil moisture calculation in advance starts exactly 90 days before sowing. This is used for crop 90 (winter wheat) in EUR. BIOMA reads the value from field        # POTENTIAL_WATER_STARTDATE of table L_SOIL_INITIAL_WATER.
        #
        # CALC_SOILWATER_BEFORE_SOWING = 2: soil moisture calculation based on fake crop (used for the RUK crops). This behavior was copied from ISW.
        #
        # CALC_SOILWATER_BEFORE_SOWING = 3 (new): the soil moisture calculation in advance starts at a fixed date, independently from the sowing date. The calculation in advance is stopped automatically at the sowing date. The start date is the value of the field POTENTIAL_WATER_STARTDATE of table L_SOIL_INITIAL_WATER. This case         # will be used for the new crop maize parametrization (crop 98), for which the soil water calculation starts        # at the first of October of the year before sowing, for every grid cell.
        #
        # Note: There is nothing in the model code that, in case CALC_SOILWATER_BEFORE_SOWING = 1, sets the start exactly 90 days before
        # the sowing. In fact, cases 1 and 3 are equivalent in terms of Ecrops code as we run it for the CGMS23
        # lines. Both the cases read the initial date from column POTENTIAL_WATER_STARTDATE  and both read the
        # initial quantity of water in soil from column ROOTING_DEPTH_POT_WATER_ISV. In both cases the water balance
        # in advance stops at sowing/emergence. Anyway it is better to keep the distinction to remember that the
        # values in the tables were stored according to two different logics: in case 1 (associated to crop 90) we
        # set the POTENTIAL_WATER_STARTDATE  90 days before the sowing and the ROOTING_DEPTH_POT_WATER_ISV is
        # calculated according to an average value in case 3 (associated to crop 98) we set the
        # POTENTIAL_WATER_STARTDATE at 1st of October and the ROOTING_DEPTH_POT_WATER_ISV  is set to 0 (starts at
        # wilting point)
        status.layeredwaterbalance.parameters.PerformWaterBalanceStartInAdvance = 'CALC_SOILWATER_BEFORE_SOWING' in status.allparameters and \
                                                                                  status.allparameters[
                                                                                      'CALC_SOILWATER_BEFORE_SOWING'] == 1
        status.layeredwaterbalance.parameters.PerformWaterBalanceStartInAdvanceUntilSowing = 'CALC_SOILWATER_BEFORE_SOWING' in status.allparameters and \
                                                                                             status.allparameters[
                                                                                                 'CALC_SOILWATER_BEFORE_SOWING'] == 3
        return status

    def IsWaterBalanceStarted(self, status):
        """
        return true if, according to the type of water balance start, the water balance is already started at the current day
        :param status:
        :return: true if started, false otherwise
        """
        if status.layeredwaterbalance.parameters.PerformWaterBalanceStartInAdvance:
            if status.POTENTIAL_WATER_STARTDATE_date is None:
                raise Exception(
                    "Error running LayeredWaterBalance with option 'PerformWaterBalanceStartInAdvance': POTENTIAL_WATER_STARTDATE is None!")
            return status.POTENTIAL_WATER_STARTDATE_date <= status.day
        else:
            if status.layeredwaterbalance.parameters.PerformWaterBalanceStartInAdvanceUntilSowing:
                if status.POTENTIAL_WATER_STARTDATE_date is None:
                    raise Exception(
                        "Error running LayeredWaterBalance with option 'PerformWaterBalanceStartInAdvance': POTENTIAL_WATER_STARTDATE is None!")
                return status.POTENTIAL_WATER_STARTDATE_date <= status.day
            else:
                return status.sowing_emergence_day <= status.day

    def InitialWaterForWaterBalanceStart(self, status):
        """
        return the amount of water to be set in soil at the initialization of the water balance, according to the type of water balance start
        :param status:
        :return: the amount of water
        """
        if status.layeredwaterbalance.parameters.PerformWaterBalanceStartInAdvance or status.layeredwaterbalance.parameters.PerformWaterBalanceStartInAdvanceUntilSowing:
            if isnan(status.soildata[
                         'ROOTING_DEPTH_POT_WATER_ISV']):  # if ISV is nan, we use the max water in soil FC_WAV
                return status.soildata['FC_WAV']
            else:
                return status.soildata['ROOTING_DEPTH_POT_WATER_ISV']
        else:
            return status.soildata['WAV']

    def determine_rooting_status(self, RD, RDM, layers):
        """Determines the rooting status of the soil layers and update layer weights.

        Soil layers can be rooted, partially rooted, potentially rooted or never rooted.
        This is stored in layer.rooting_status

        Note that this routine expected that the maximum rooting depth coincides
        with a layer boundary.

        :param RD:the current rooting depth
        :param RDM: the maximum rooting depth
        """
        upper_layer_boundary = 0
        lower_layer_boundary = 0
        l=0
        for layer in layers:
            lower_layer_boundary += layer.TSL
            if lower_layer_boundary <= RD:
                layer.rooting_status = "rooted"
            elif upper_layer_boundary < RD < lower_layer_boundary:
                layer.rooting_status = "partially rooted"
            elif RD < lower_layer_boundary <= RDM:
                layer.rooting_status = "potentially rooted"
            else:
                layer.rooting_status = "never rooted"
            upper_layer_boundary = lower_layer_boundary
            l+=1

        self._compute_layer_weights(RD,layers)

    def _compute_layer_weights(self, RD, layers):
        """computes the layer weights given the current rooting depth.

        :param RD: The current rooting depth
        """
        lower_layer_boundary = 0
        for layer in layers:
            lower_layer_boundary += layer.TSL
            if layer.rooting_status == "rooted":
                layer.Wtop = 1.0
                layer.Wpot = 0.0
                layer.Wund = 0.0
            elif layer.rooting_status == "partially rooted":
                layer.Wtop = 1.0 - (lower_layer_boundary - RD) / layer.TSL
                layer.Wpot = 1.0 - layer.Wtop
                layer.Wund = 0.0
            elif layer.rooting_status == "potentially rooted":
                layer.Wtop = 0.0
                layer.Wpot = 1.0
                layer.Wund = 0.0
            elif layer.rooting_status == "never rooted":
                layer.Wtop = 0.0
                layer.Wpot = 0.0
                layer.Wund = 1.0
            else:
                msg = "Unknown rooting status: %s" % layer.rooting_status
                raise Exception(msg)

    def validate_max_rooting_depth(self, RDM, layers):
        """Validate that the maximum rooting depth coincides with a layer boundary.

        :param RDM: The maximum rootable depth
        :return: True or False
        """
        tiny = 0.01
        lower_layer_boundary = 0
        for layer in layers:
            lower_layer_boundary += layer.TSL
            if abs(RDM - lower_layer_boundary) < tiny:
                break
        else:  # no break
            msg = "Current maximum rooting depth (%f) does not coincide with a layer boundary!" % RDM
            raise Exception(msg)

    def get_max_rootable_depth(self,layers):
        """Returns the maximum soil rootable depth.

        here we assume that the max rootable depth is equal to the lower boundary of the last layer.

        :return: the max rootable depth in cm
        """
        LayerThickness = [l.TSL for l in layers]
        LayerLowerBoundary = list(np.cumsum(LayerThickness))
        return max(LayerLowerBoundary)

    def initialize(self, status):
        s = status.layeredwaterbalance.states
        p = status.layeredwaterbalance.parameters
        r = status.layeredwaterbalance.rates

        # in this version Groundwater influence is not yet implemented
        if p.GW:
            raise NotImplementedError("Groundwater influence not yet implemented.")

        #initialization of some output variables
        RD = 0
        s.SMUR = 0
        s.SUMSM = 0

        # Maximum rootable depth
        RDMsoil = self.get_max_rootable_depth(p.SOIL_LAYERS)
        #s.RDM =  min(p.RDMCR, RDMsoil)
        s.RDM = RDMsoil  #new in  1.7.7

        self.validate_max_rooting_depth(s.RDM,p.SOIL_LAYERS)

        #check that current root depth does not exceed max root depth
        if RD > s.RDM:
            msg = ("rooting depth %f exceeeds maximum rooting depth %f" %
                   (RD, s.RDM))
            raise Exception(msg)

        self.determine_rooting_status(RD, s.RDM, p.SOIL_LAYERS)

        s.RD = RD
        # save old rooting depth (for testing on growth in integration)
        s._RDold = RD
        s.SS = p.SSI  # Initial surface storage




        # AVMAX -  maximum available content of layer(s)
        # This is calculated first to achieve an even distribution of water in the rooted top
        # if WAV is small. Note the separate limit for initial SM in the rooted zone.

        TOPLIM = 0.0
        LOWLIM = 0.0
        AVMAX = []
        for il, layer in enumerate(p.SOIL_LAYERS):
            if layer.rooting_status in ["rooted", "partially rooted"]:

                # Check whether SMLIM is within boundaries
                SML = limit(layer.SMW, layer.SM0, p.SMLIM)

                AVMAX.append((SML - layer.SMW) * layer.TSL)  # available in cm
                # also if partly rooted, the total layer capacity counts in TOPLIM
                # this means the water content of layer ILR is set as if it would be
                # completely rooted. This water will become available after a little
                # root growth and through numerical mixing each time step.
                TOPLIM += AVMAX[il]
            elif layer.rooting_status == "potentially rooted":
                # below the rooted zone the maximum is saturation (see code for WLOW in one-layer model)
                # again the full layer capacity adds to LOWLIM.
                SML = layer.SM0

                AVMAX.append((SML - layer.SMW) * layer.TSL)  # available in cm
                LOWLIM += AVMAX[il]
            else:  # Below the potentially rooted zone
                break

        # get WAV in function of the type of soil moisture calculation
        WAV = self.InitialWaterForWaterBalanceStart(status)


        if WAV <= 0.0:
            # no available water
            TOPRED = 0.0
            LOWRED = 0.0
        elif WAV <= TOPLIM:
            # available water fits in layer(s) 1..ILR, these layers are rooted or almost rooted
            # reduce amounts with ratio WAV / TOPLIM
            TOPRED = WAV / TOPLIM
            LOWRED = 0.0
        elif WAV < TOPLIM + LOWLIM:
            # available water fits in potentially rooted layer
            # rooted zone is filled at capacity ; the rest reduced
            TOPRED = 1.0
            LOWRED = (WAV - TOPLIM) / LOWLIM
        else:
            # water does not fit ; all layers "full"
            TOPRED = 1.0
            LOWRED = 1.0

        W = 0.0
        WAVUPP = 0.0
        WLOW = 0.0
        WAVLOW = 0.0


        Flow = np.zeros(len(p.SOIL_LAYERS) + 1)
        for il, layer in enumerate(p.SOIL_LAYERS):
            if layer.rooting_status in ["rooted", "partially rooted"]:
                # Part of the water assigned to ILR may not actually be in the rooted zone, but it will
                # be available shortly through root growth (and through numerical mixing).
                p.SOIL_LAYERS[il].SM = layer.SMW + AVMAX[il] * TOPRED / layer.TSL

                W += p.SOIL_LAYERS[il].SM * layer.TSL * layer.Wtop
                WLOW += p.SOIL_LAYERS[il].SM * layer.TSL * layer.Wpot
                # available water
                WAVUPP += (p.SOIL_LAYERS[il].SM - layer.SMW) * layer.TSL * layer.Wtop
                WAVLOW += (p.SOIL_LAYERS[il].SM - layer.SMW) * layer.TSL * layer.Wpot
            elif layer.rooting_status == "potentially rooted":

                p.SOIL_LAYERS[il].SM = layer.SMW + AVMAX[il] * LOWRED / layer.TSL

                WLOW += p.SOIL_LAYERS[il].SM * layer.TSL * layer.Wpot
                # available water
                WAVLOW += (p.SOIL_LAYERS[il].SM - layer.SMW) * layer.TSL * layer.Wpot
            else:
                # below the maximum rooting depth, set SM content to wilting point
                p.SOIL_LAYERS[il].SM = layer.SMW
            p.SOIL_LAYERS[il].WC = p.SOIL_LAYERS[il].SM * layer.TSL


            # set groundwater depth far away for clarity ; this prevents also
            # the root routine to stop root growth when they reach the groundwater
            ZT = 999.0

        r.Flow = Flow

        # Initial values for profile water content
        s._WCI = 0
        for il, layer in enumerate(p.SOIL_LAYERS):
            s._WCI+=p.SOIL_LAYERS[il].WC

        # water content for each layer + a few fixed points often used
        for il, layer in enumerate(p.SOIL_LAYERS):
            p.SOIL_LAYERS[il].WC0 = p.SOIL_LAYERS[il].SM0 * p.SOIL_LAYERS[il].TSL
            p.SOIL_LAYERS[il].WCW = p.SOIL_LAYERS[il].SMW * p.SOIL_LAYERS[il].TSL
            p.SOIL_LAYERS[il].WCFC = p.SOIL_LAYERS[il].SMFCF * p.SOIL_LAYERS[il].TSL
            p.SOIL_LAYERS[il].CondFC = 10.0 ** p.SOIL_LAYERS[il].CONTAB(self.PFFC)
            p.SOIL_LAYERS[il].CondK0 = 10.0 ** p.SOIL_LAYERS[il].CONTAB(self.PFSAT)
            # dfumagalli - 20-03-2024 - added calculation of RSM
            # RSM of single horizon = 100* (SM - wilting point)/ (field capacity - wilting point)
            p.SOIL_LAYERS[il].RSM = 100 * (p.SOIL_LAYERS[il].SM - p.SOIL_LAYERS[il].SMW) / (
                    p.SOIL_LAYERS[il].SMFCF - p.SOIL_LAYERS[il].SMW)

        # soil evaporation, days since last rain
        s.DSLR = 1.0
        if p.SOIL_LAYERS[0].SM <= (p.SOIL_LAYERS[0].SMW + \
                                   0.5 * (p.SOIL_LAYERS[0].SMFCF - \
                                          p.SOIL_LAYERS[0].SMW)):
            s.DSLR = 5.0

        # SM_MEAN is the average soil moisture in the rooted zone
        s.SM_MEAN = 0
        if s.RD > 0:
            s.SM_MEAN = s.W / s.RD
        else:  # if root depth is zero (so, before emergence) we set the SM_MEAN equal to the SM_MEAN of the first layer, to not leave the SM_MEAN equal to zero. The same for RSM.
            s.SM_MEAN = p.SOIL_LAYERS[0].SM
            s.RSM_rooted_zone = p.SOIL_LAYERS[0].RSM



        s.RINold = 0.
        s.WTRAP = 0.0
        r.WTRAL = np.zeros(p.NSL)
        s.WTRAT = 0.0
        s.EVST = 0.0
        s.EVWT = 0.0
        s.TSR = 0.0
        s.RAINT = 0.0
        s.WDRT = 0.0
        s.TOTINF = 0.0
        s.TOTIRR = 0.0
        s.SUMSM = 0.0
        s.PERCT = 0.0
        s.LOSST = 0.0
        s.BOTTOMFLOWT = 0.0
        s.RunOff = 0.0
        s.IN = 0.0
        s.CRT = 0.0
        s.DRAINT = 0.0
        s.WBOT = 0.0
        s.WSUB = 0.0,
        s.WBALRT = -999.0
        s.WBALTT = -999.0
        r.RIRR = 0
        s.W = W
        s.WAVUPP = 0
        s.WLOW = WLOW
        s.WAVLOW = WAVLOW
        r.DWBOT = 0
        s.WWLOWI = 0
        s.WLOWDRT = 0
        r.SR = 0
        s.flag_crop_emerged = False
        return status

    def runstep(self, status):
        s = status.layeredwaterbalance.states
        p = status.layeredwaterbalance.parameters
        r = status.layeredwaterbalance.rates

        # execute only after water balance calculation must be started
        if not self.IsWaterBalanceStarted(status):
            return status

        # Maximum upward flow is 50% of amount needed to reach equilibrium between layers
        # see documentation Kees Rappoldt - page 80
        UpwardFlowLimit = 0.5

        # Max number of flow iterations and precision required
        MaxFlowIter = 50
        TinyFlow = 0.001

        DELT = 1
        RD = s.RD
        if RD != self.RDold and self.RDold > 0:
            msg = "Rooting depth changed unexpectedly"
            raise RuntimeError(msg)

        # Transpiration and maximum soil and surfacewater evaporation rates
        # are calculated by the crop Evapotranspiration module.
        # However, if the crop is not yet emerged then set TRA=0 and use
        # the potential soil/water evaporation rates directly because there is
        # no shading by the canopy.
        if s.flag_crop_emerged is True:

            r.WTRA = r.TRA
            EVWMX = r.EVWMX
            EVSMX = r.EVSMX
            r.WTRAL = r.TRALY

        else:
            r.WTRA = 0.
            r.WTRAL = np.zeros(p.NSL)
            EVWMX = r.E0
            EVSMX = r.ES0
        # ------------------------------------------

        # actual evaporation rates ...
        r.EVW = 0.
        r.EVS = 0.
        # ... from surface water if surface storage more than 1 cm, ...
        if s.SS > 1.:
            r.EVW = EVWMX
        else:  # ... else from soil surface
            if s.RINold >= 1.:  # RIN not set, must be RIN from previous 'call'
                r.EVS = EVSMX
                s.DSLR = 1.
            else:
                EVSMXT =  EVSMX * (sqrt(s.DSLR + 1) - sqrt(s.DSLR)) #in the old version it was (sqrt(s.DSLR ) - sqrt(s.DSLR-1.))
                r.EVS = min(EVSMX, EVSMXT + s.RINold)
                s.DSLR += 1.


        # conductivities and Matric Flux Potentials for all layers
        PF = np.zeros(p.NSL)
        Conductivity = np.zeros(p.NSL)
        MatricFluxPot = np.zeros(p.NSL)
        EquilWater = np.zeros(p.NSL)
        for il in range(0, p.NSL):
            PF[il] = p.SOIL_LAYERS[il].PFTAB(p.SOIL_LAYERS[il].SM)
            # print "layer %i: PF %f SM %f" % (il, PF[il], p.SOIL_LAYERS[il].SM)
            Conductivity[il] = 10.0 ** p.SOIL_LAYERS[il].CONTAB(PF[il])
            MatricFluxPot[il] = p.SOIL_LAYERS[il].MFPTAB(PF[il])


        # Potentially infiltrating rainfall
        if p.IFUNRN == 0:
            RINPRE = (1. - p.NOTINF) * r.RAIN

        else:
            # infiltration is function of storm size (NINFTB)
            RINPRE = (1. - p.NOTINF * p.NINFTB(r.RAIN)) * r.RAIN

        # Second stage preliminary infiltration rate (RINPRE)
        # including surface storage and irrigation
        RINPRE = RINPRE + r.RIRR + s.SS
        if s.SS > 0.1:
            # with surface storage, infiltration limited by SOPE (SOPE = surface conductivity)
            AVAIL = RINPRE + r.RIRR - r.EVW
            RINPRE = min(p.SOIL_LAYERS[0].SOPE, AVAIL)



        # maximum flow at Top Boundary of each layer
        # ------------------------------------------
        # DOWNWARD flows are calculated in two ways,
        # (1) a "dry flow" from the matric flux potentials
        # (2) a "wet flow" under the current layer conductivities and downward gravity.
        # Clearly, only the dry flow may be negative (=upward). The dry flow accounts for the large
        # gradient in potential under dry conditions (but neglects gravity). The wet flow takes into
        # account gravity only and will dominate under wet conditions. The maximum of the dry and wet
        # flow is taken as the downward flow, which is then further limited in order the prevent
        # (a) oversaturation and (b) water content to decrease below field capacity.
        #
        # UPWARD flow is just the dry flow when it is negative. In this case the flow is limited
        # to a certain fraction of what is required to get the layers at equal potential, taking
        # into account, however, the contribution of an upward flow from further down. Hence, in
        # case of upward flow from the groundwater, this upward flow is propagated upward if the
        # suction gradient is sufficiently large.

        EVflow = np.zeros(p.NSL + 1)  # 1 more
        FlowMX = np.zeros(p.NSL + 1)  # 1 more
        Flow = np.zeros(p.NSL + 1)  # 1 more


        for il in range(0, p.NSL):
            p.SOIL_LAYERS[il].DWC = 0.0  # water change



        # Bottom layer conductivity limits the flow. Below field capacity there is no
        # downward flow, so downward flow through lower boundary can be guessed as
        FlowMX[p.NSL] = max(p.SOIL_LAYERS[p.NSL - 1].CondFC, Conductivity[p.NSL - 1])

        # drainage
        r.DMAX = 0.0

        LIMWET = np.zeros(p.NSL)
        LIMDRY = np.zeros(p.NSL)

        for il in range(p.NSL - 1, -1, -1):

            # limiting DOWNWARD flow rate
            # == wet conditions: the soil conductivity is larger
            #    the soil conductivity is the flow rate for gravity only
            #    this limit is DOWNWARD only
            # == dry conditions: the MFP gradient
            #    the MFP gradient is larger for dry conditions
            #    allows SOME upward flow
            if il == 0:
                LIMWET[il] = p.SOIL_LAYERS[0].SOPE
                LIMDRY[il] = 0.0
            else:

                # compute dry flow given gradients in matric flux potential

                # same soil type
                if p.SOIL_LAYERS[il - 1].SOIL_GROUP_NO == p.SOIL_LAYERS[il].SOIL_GROUP_NO:
                    # flow rate estimate from gradient in Matric Flux Potential
                    LIMDRY[il] = 2.0 * (MatricFluxPot[il - 1] - MatricFluxPot[il]) / (
                            p.SOIL_LAYERS[il - 1].TSL + p.SOIL_LAYERS[il].TSL)
                    if LIMDRY[il] < 0.0:
                        # upward flow rate ; amount required for equal water content is required below
                        MeanSM = (p.SOIL_LAYERS[il - 1].WC + p.SOIL_LAYERS[il].WC) / (
                                p.SOIL_LAYERS[il - 1].TSL + p.SOIL_LAYERS[il].TSL)
                        EqualPotAmount = p.SOIL_LAYERS[il - 1].WC - p.SOIL_LAYERS[
                            il - 1].TSL * MeanSM  # should be negative like the flow

                else:  # different soil types
                    # iterative search to PF at layer boundary (by bisection)
                    PF1 = PF[il - 1]
                    PF2 = PF[il]
                    MFP1 = MatricFluxPot[il - 1]
                    MFP2 = MatricFluxPot[il]
                    for i in range(0, MaxFlowIter):
                        PFx = (PF1 + PF2) / 2.0
                        Flow1 = 2.0 * (+ MFP1 - p.SOIL_LAYERS[il - 1].MFPTAB(PFx)) / p.SOIL_LAYERS[il - 1].TSL
                        Flow2 = 2.0 * (- MFP2 + p.SOIL_LAYERS[il].MFPTAB(PFx)) / p.SOIL_LAYERS[il].TSL
                        if abs(Flow1 - Flow2) < TinyFlow:  # sufficient accuracy
                            break
                        elif abs(Flow1) > abs(Flow2):
                            # flow in layer 1 is larger ; PFx must shift in the direction of PF1
                            PF2 = PFx
                        elif abs(Flow1) < abs(Flow2):
                            # flow in layer 2 is larger ; PFx must shift in the direction of PF2
                            PF1 = PFx

                    if i >= MaxFlowIter:
                        msg = "LIMDRY flow iteration failed"
                        raise RuntimeError(msg)

                    LIMDRY[il] = (Flow1 + Flow2) / 2.0
                    if LIMDRY[il] < 0.0:
                        # upward flow rate ; amount required for equal potential is required below
                        Eq1 = -p.SOIL_LAYERS[il].WC
                        Eq2 = 0.0
                        for i in range(0, MaxFlowIter):
                            EqualPotAmount = (Eq1 + Eq2) / 2.0
                            SM1 = (p.SOIL_LAYERS[il - 1].WC - EqualPotAmount) / p.SOIL_LAYERS[il - 1].TSL
                            SM2 = (p.SOIL_LAYERS[il].WC + EqualPotAmount) / p.SOIL_LAYERS[il].TSL
                            PF1 = p.SOIL_LAYERS[il - 1].SMTAB(SM1)
                            PF2 = p.SOIL_LAYERS[il].SMTAB(SM2)
                            if abs(Eq1 - Eq2) < TinyFlow:  # sufficient accuracy
                                break
                            elif PF1 > PF2:  # suction in top layer larger; absolute amount should be larger
                                Eq2 = EqualPotAmount
                            else:  # suction in bottom layer larger; absolute amount should be reduced
                                Eq1 = EqualPotAmount

                        if i >= MaxFlowIter:
                            msg = "Limiting amount iteration failed"
                            raise RuntimeError(msg)

                # the limit under wet conditions in a unit gradient
                LIMWET[il] = (p.SOIL_LAYERS[il - 1].TSL + p.SOIL_LAYERS[il].TSL) \
                             / (p.SOIL_LAYERS[il - 1].TSL / Conductivity[il - 1] + p.SOIL_LAYERS[il].TSL /
                                Conductivity[il])

            FlowDown = True  # default



            if LIMDRY[il] < 0.0:
                # upward flow (negative !) is limited by fraction of amount required for equilibrium
                FlowMax = max(LIMDRY[il], EqualPotAmount * UpwardFlowLimit)
                if il > 0:
                    # upward flow is limited by amount required to bring target layer at equilibrium/field capacity
                    # free drainage
                    FCequil = p.SOIL_LAYERS[il - 1].WCFC

                    TargetLimit = r.WTRAL[il - 1] + (FCequil - p.SOIL_LAYERS[il - 1].WC) / DELT
                    if TargetLimit > 0.0:
                        # target layer is "dry": below field capacity ; limit upward flow
                        FlowMax = max(FlowMax, -1.0 * TargetLimit)
                        # there is no saturation prevention since upward flow leads to a decrease of p.SOIL_LAYERS[il].WC
                        # instead flow is limited in order to prevent a negative water content
                        FlowMX[il] = max(FlowMax, FlowMX[il + 1] + r.WTRAL[il] - p.SOIL_LAYERS[il].WC / DELT)
                        FlowDown = False
                    else:
                        # Target layer is "wet", above field capacity, without groundwater.
                        # The free drainage model implies that upward flow is rejected here.
                        # Downward flow is enabled and the free drainage model applies.
                        FlowDown = True

            if FlowDown:
                # maximum downward flow rate (LIMWET is always a positive number)
                FlowMax = max(LIMDRY[il], LIMWET[il])
                # this prevents saturation of layer il
                # maximum top boundary flow is bottom boundary flow plus saturation deficit plus sink
                FlowMX[il] = min(FlowMax,
                                 FlowMX[il + 1] + (p.SOIL_LAYERS[il].WC0 - p.SOIL_LAYERS[il].WC) / DELT + r.WTRAL[
                                     il])

        # adjustment of infiltration rate to prevent saturation
        r.RIN = min(RINPRE, FlowMX[0])

        # contribution of layers to soil evaporation in case of drought upward flow is allowed
        EVSL = np.zeros(p.NSL)
        EVSL[0] = min(r.EVS, (p.SOIL_LAYERS[0].WC - p.SOIL_LAYERS[0].WCW) / DELT + r.RIN - r.WTRAL[0])

        EVrest = r.EVS - EVSL[0]
        for il in range(1, p.NSL):
            Available = max(0.0, (p.SOIL_LAYERS[il].WC - p.SOIL_LAYERS[il].WCW) / DELT - r.WTRAL[il])
            if Available >= EVrest:
                EVSL[il] = EVrest
                EVrest = 0.0
                break
            else:
                EVSL[il] = Available
                EVrest = EVrest - Available

        # reduce evaporation if entire profile becomes airdry
        # there is no evaporative flow through lower boundary of layer NSL
        r.EVS -= EVrest

        # Convert contribution of soil layers to EVS as an upward flux
        EVflow[0] = r.EVS
        for il in range(1, p.NSL):
            EVflow[il] = EVflow[il - 1] - EVSL[il - 1]
        EVflow[p.NSL] = 0.0 # see comment above

        # limit downward flows as to not get below field capacity / equilibrium content
        Flow[0] = r.RIN - EVflow[0]
        for il in range(0, p.NSL):
            #free drainage
            WaterLeft = p.SOIL_LAYERS[il].WCFC
            MXLOSS = (p.SOIL_LAYERS[il].WC - WaterLeft) / DELT  # maximum loss
            Excess = max(0.0, MXLOSS + Flow[il] - r.WTRAL[il])  # excess of water (positive)
            Flow[il + 1] = min(FlowMX[il + 1], Excess - EVflow[il + 1])  # note that a negative (upward) flow is not affected

            # rate of change
            p.SOIL_LAYERS[il].DownwardFLOWAtBottomOfLayer = Flow[il]
            p.SOIL_LAYERS[il].DWC = Flow[il] - Flow[il + 1] - r.WTRAL[il]


        # Flow at the bottom of the profile
        r.BOTTOMFLOW = Flow[-1]

        # Computation of rate of change in surface storage and surface runoff
        # SStmp is the layer of water that cannot infiltrate and that can potentially
        # be stored on the surface. Here we assume that RAIN_NOTINF automatically
        # ends up in the surface storage (and finally runoff).
        SStmp = r.RAIN + r.RIRR - r.EVW - r.RIN
        # rate of change in surface storage is limited by SSMAX - SS
        r.DSS = min(SStmp, (p.SSMAX - s.SS))
        # Remaining part of SStmp is send to surface runoff
        r.DTSR = SStmp - r.DSS
        # incoming rainfall rate
        r.DRAINT = r.RAIN

        #set RINold as current RIN
        s.RINold=r.RIN

        

        return status

    def integrate(self, status):
        s = status.layeredwaterbalance.states
        p = status.layeredwaterbalance.parameters
        r = status.layeredwaterbalance.rates

        # execute only after water balance calculation must be started and when the runstep method has been run
        if not self.IsWaterBalanceStarted(status) or not hasattr(r, 'EVW'):
            return status


        DELT = 1  # daily step delta is 1

        # !-----------------------------------------------------------------------
        # ! integrals of the water balance:  summation and state variables
        # !-----------------------------------------------------------------------

        # amount of water in soil layers ; soil moisture content
        for il in range(0, p.NSL):
            p.SOIL_LAYERS[il].WC += p.SOIL_LAYERS[il].DWC * DELT
            p.SOIL_LAYERS[il].SM = p.SOIL_LAYERS[il].WC / p.SOIL_LAYERS[il].TSL

            # dfumagalli - 20-03-2024 - added calculation of RSM
            # RSM of single horizon = 100* (SM - wilting point)/ (field capacity - wilting point)
            p.SOIL_LAYERS[il].RSM = 100 * (p.SOIL_LAYERS[il].SM - p.SOIL_LAYERS[il].SMW) / (
                    p.SOIL_LAYERS[il].SMFCF - p.SOIL_LAYERS[il].SMW)



        # totals of transpirations
        if hasattr(status.rates, 'TRAMX'):
            s.WTRAP += status.rates.TRAMX  # potential transpiration

        if s.flag_crop_emerged is True:
            s.WTRAT += sum(r.WTRAL) * DELT  # actual crop transpiration

        # evaporation from surface water layer and/or soil
        s.EVWT += r.EVW * DELT
        s.EVST += r.EVS * DELT

        # totals of rainfall, irrigation and infiltration
        s.RAINT += r.RAIN * DELT
        s.TOTINF += r.RIN * DELT
        s.TOTIRR += r.RIRR * DELT

        # totals of surface storage and runoff
        s.SS += r.DSS * DELT
        s.TSR += r.DTSR * DELT


        # total of loss of water by outflow through bottom of profile
        s.BOTTOMFLOWT += r.BOTTOMFLOW * DELT

        # percolation from rootzone
        # without groundwater this flow is always called percolation
        s.CRT = 0.0

        # change of rootzone
        if abs(s.RD - s._RDold) > 0.001:
            self.determine_rooting_status(s.RD, s.RDM,p.SOIL_LAYERS)

        # compute summary values of water for rooted, potentially rooted and unrooted soil compartments
        W = 0.0
        WAVUPP = 0.0
        WLOW = 0.0
        WAVLOW = 0.0
        WBOT = 0.0
        WAVBOT = 0.0
        # get W and WLOW and available water amounts
        for il, layer in enumerate(p.SOIL_LAYERS):
            W += p.SOIL_LAYERS[il].WC * layer.Wtop
            WLOW += p.SOIL_LAYERS[il].WC * layer.Wpot
            WBOT += p.SOIL_LAYERS[il].WC * layer.Wund
            WAVUPP += (p.SOIL_LAYERS[il].WC - layer.WCW) * layer.Wtop
            WAVLOW += (p.SOIL_LAYERS[il].WC - layer.WCW) * layer.Wpot
            WAVBOT += (p.SOIL_LAYERS[il].WC - layer.WCW) * layer.Wund

        # Update states of water
        s.W = W
        s.WLOW = WLOW
        s.WWLOW = s.W + s.WLOW
        s.WBOT = WBOT
        s.WAVUPP = WAVUPP
        s.WAVLOW = WAVLOW
        s.WAVBOT = WAVBOT

        # save rooting depth for which layer contents have been determined
        s._RDold = s.RD

        #SM_MEAN is the average soil moisture in the rooted zone
        if s.RD>0:
            s.SM_MEAN = s.W / s.RD
        else:# if root depth is zero (so, before emergence) we set the SM_MEAN equal to the SM_MEAN of the first layer, to not leave the SM_MEAN equal to zero
            s.SM_MEAN = p.SOIL_LAYERS[0].SM

        WCsum = 0
        for il, layer in enumerate(p.SOIL_LAYERS):
            WCsum +=p.SOIL_LAYERS[il].WC

        # checksums waterbalance for system Free Drainage version
        checksum = (p.SSI - s.SS  # change in surface storage
                    + s._WCI - WCsum  # Change in soil water content

                    + s.RAINT + s.TOTIRR  # inflows to the system
                    - s.WTRAT - s.EVWT - s.EVST - s.TSR - s.BOTTOMFLOWT  # outflows from the system
                    )
        if abs(checksum) > 0.001:
            msg = "Waterbalance not closing on %s with checksum: %f" % (status.day, checksum)
            raise Exception(msg)
            print(msg)


        #to return the old name of loss to subsoil
        s.LOSST = s.BOTTOMFLOWT

        # dfumagalli - 20-03-2024 - added calculation of RSM
        # RSM of the rooted zone is calculated as weighted average of the RSM of the horizons, where the weights are the horizon thicknesses.
        # (For the last horizon touched we use the root depth inside the horizon instead of the total horizon thickness.)
        if s.RD == 0:  # if root depth is zero (so, before emergence) we set the RSM equal to the RSM of the first layer, to not leave the RSM equal to zero
            s.RSM_rooted_zone = p.SOIL_LAYERS[0].RSM
        else:
            tmp_rsm_rooted = 0
            tmp_thickness_layer_rooted = 0
            for il in range(0, p.NSL):  # for all the layers
                if s.RD < p.SOIL_LAYERS[il].LBSL - p.SOIL_LAYERS[il].TSL:  # not rooted layer
                    break
                else:
                    if s.RD < p.SOIL_LAYERS[il].LBSL:  # partially rooted layer
                        thickness_layer_rooted = s.RD - (p.SOIL_LAYERS[il].LBSL - p.SOIL_LAYERS[
                            il].TSL)  # rooted thickness =  root depth - (lower depth - layer thickness)
                    else:  # fully rooted layer
                        thickness_layer_rooted = p.SOIL_LAYERS[il].TSL  # rooted thickness = layer thickness
                tmp_rsm_rooted += p.SOIL_LAYERS[il].RSM * thickness_layer_rooted
                tmp_thickness_layer_rooted += thickness_layer_rooted
            if s.RD != tmp_thickness_layer_rooted:
                raise Exception(
                    'Unexpected error in RSM calculation: thickness layer rooted is not equal to root depth')
            s.RSM_rooted_zone = tmp_rsm_rooted / s.RD




        return status

    def _layer_weights(self, RD, RDM, ILR, ILM, NSL, SOIL_LAYERS):
        """Calculate weight factors for rooted- and sub-layer calculations
        """
        # RD    the rooting depth
        # ILR   deepest layer containing roots
        # ILM   deepest layer that will contain roots
        # RDM   max rooting depth aligned to soil layer boundary

        # NSL   number of layers
        # TSL   the layerthickness
        # LBSL  the Lower Boundaries of the NSL soil layers
        # Wtop  weights for contribution to rootzone
        # Wpot  weights for contribution to potentially rooted zone
        # Wund  weights for contribution to never rooted layers

        sl = SOIL_LAYERS

        # print "---\nlayer_weights NSL: %i ILR: %i ILM: %i RD: %f RDM: %f\n---" % \
        # (NSL, ILR, ILM, RD, RDM)

        for il in range(0, NSL):
            # rooted layer
            if (il < ILR):
                sl[il].Wtop = 1.0
                sl[il].Wpot = 0.0
                sl[il].Wund = 0.0

            # partly rooted
            elif (il == ILR and il < ILM):  # at the end fully rooted
                sl[il].Wtop = 1.0 - (sl[il].LBSL - RD) / sl[il].TSL
                sl[il].Wpot = 1.0 - sl[il].Wtop
                sl[il].Wund = 0.0
            elif (il == ILR and il == ILM):  # at the end partly rooted
                sl[il].Wtop = 1.0 - (sl[il].LBSL - RD) / sl[il].TSL
                sl[il].Wund = (sl[il].LBSL - RDM) / sl[il].TSL
                sl[il].Wpot = 1.0 - sl[il].Wund - sl[il].Wtop

            # not rooted
            elif (il < ILM):  # at the end fully rooted
                sl[il].Wtop = 0.0
                sl[il].Wpot = 1.0
                sl[il].Wund = 0.0
            elif (il == ILM):  # at the end partly rooted
                sl[il].Wtop = 0.0
                sl[il].Wund = (sl[il].LBSL - RDM) / sl[il].TSL
                sl[il].Wpot = 1.0 - sl[il].Wund

            # never rooted
            else:
                sl[il].Wtop = 0.0
                sl[il].Wpot = 0.0
                sl[il].Wund = 1.0

                # msg = 'layer %i: %f %f weights top %f pot %f und %f' % \
                #       (il, sl[il].TSL, sl[il].LBSL, \
                #        sl[il].Wtop, sl[il].Wpot, sl[il].Wund)
                # print msg

    def _SUBSOL(self, PF, D, CONTAB):
        """SUBSOL...
        """

        DEL = np.zeros(4)
        PFGAU = np.zeros(12)
        HULP = np.zeros(12)
        CONDUC = np.zeros(12)

        ELOG10 = 2.302585
        LOGST4 = 2.518514

        START = np.array([0, 45, 170, 330])
        PFSTAN = np.array([0.705143, 1.352183, 1.601282, 1.771497, 2.031409, \
                           2.192880, 2.274233, 2.397940, 2.494110])
        PGAU = np.array([0.1127016654, 0.5, 0.8872983346])
        WGAU = np.array([0.2777778, 0.4444444, 0.2777778])

        # calculation of matric head and check on small pF
        PF1 = PF
        D1 = D
        MH = exp(ELOG10 * PF1)

        if PF1 <= 0.:
            # in case of small matric head
            K0 = exp(ELOG10 * CONTAB(-1))
            FLOW = K0 * (MH / D - 1)
        else:
            IINT = 0

            # number and width of integration intervals
            for I1 in range(0, 4):
                if I1 <= 2:
                    DEL[I1] = min(START[I1 + 1], MH) - START[I1]
                elif I1 == 3:
                    DEL[I1] = PF1 - LOGST4

                if DEL[I1] <= 0:
                    break;

                IINT += 1

            # preparation of three-point Gaussian integration
            for I1 in range(0, IINT):
                for I2 in range(0, 3):
                    I3 = (3 * I1) + I2

                    if I1 == IINT - 1:
                        # the three points in the last interval are calculated
                        if IINT <= 3:
                            PFGAU[I3] = log10(START[IINT - 1] + PGAU[I2] * DEL[IINT - 1])
                        elif IINT == 4:
                            PFGAU[I3] = LOGST4 + PGAU[I2] * DEL[IINT - 1]
                    else:
                        PFGAU[I3] = PFSTAN[I3]

                    # variables needed in the loop below
                    CONDUC[I3] = exp(ELOG10 * CONTAB(PFGAU[I3]))
                    HULP[I3] = DEL[I1] * WGAU[I2] * CONDUC[I3]

                    if I3 > 8:
                        HULP[I3] = HULP[I3] * ELOG10 * exp(ELOG10 * PFGAU[I3]);

            # 15.5 setting upper and lower limit
            FU = 1.27
            FL = -1 * exp(ELOG10 * CONTAB(PF1))
            if MH <= D1: FU = 0
            if MH >= D1: FL = 0
            if MH != D1:
                # Iteration loop
                IMAX = 3 * IINT;

                for I1 in range(0, 15):
                    FLW = (FU + FL) / 2
                    DF = (FU - FL) / 2
                    if DF < 0.01 and DF / abs(FLW) < 0.1:
                        break

                    Z = 0
                    for I2 in range(0, IMAX):
                        Z += HULP[I2] / (CONDUC[I2] + FLW)

                    if Z >= D1: FL = FLW
                    if Z <= D1: FU = FLW

            FLOW = (FU + FL) / 2

        return FLOW

    def getinputslist(self):
        return {
            "day": {"Description": "Current day", "Type": "Number", "UnitOfMeasure": "doy",
                    "StatusVariable": "status.day"},
            "flag_crop_emerged": {"Description": "True if crop emerged", "Type": "Boolean", "UnitOfMeasure": "-",
                                  "StatusVariable": "status.layeredwaterbalance.states.flag_crop_emerged"},
            "POTENTIAL_WATER_STARTDATE_date": {"Description": "Doy of start of water balance calculation",
                                               "Type": "Number",
                                               "UnitOfMeasure": "doy",
                                               "StatusVariable": "status.POTENTIAL_WATER_STARTDATE_date"},
            "soildata": {"Description": "Soil data input", "Type": "Dictionary", "UnitOfMeasure": "-",
                         "StatusVariable": "status.soildata"},

            "E0": {"Description": "Open water evapotranspiration",
                   "Type": "Number", "UnitOfMeasure": "cm",
                   "StatusVariable": "status.weather.E0"},
            "ES0": {"Description": "Bare soil evapotranspiration",
                    "Type": "Number", "UnitOfMeasure": "cm",
                    "StatusVariable": "status.weather.ES0"},

            "RD": {"Description": "Root depth", "Type": "Number", "UnitOfMeasure": "cm",
                   "StatusVariable": "status.states.RD"},

        }

    def getoutputslist(self):
        return {
            {

                "WTRA": {"Description": "Actual transpiration rate",
                         "Type": "Number", "UnitOfMeasure": "cm",
                         "StatusVariable": "status.layeredwaterbalance.rates.WTRA"},
                "EVWMX": {"Description": "Maximum evaporation rate from surface water",
                          "Type": "Number", "UnitOfMeasure": "cm",
                          "StatusVariable": "status.layeredwaterbalance.rates.EVWMX"},
                "EVSMX": {"Description": "Maximum evaporation rate from soil",
                          "Type": "Number", "UnitOfMeasure": "cm",
                          "StatusVariable": "status.layeredwaterbalance.rates.EVSMX"},
                "WTRAL": {"Description": "Actual transpiration rate for each soil layer",
                          "Type": "Array", "UnitOfMeasure": "cm",
                          "StatusVariable": "status.layeredwaterbalance.rates.WTRAL"},
                "EVW": {"Description": "Actual evaporation rate from surface water",
                        "Type": "Number", "UnitOfMeasure": "cm",
                        "StatusVariable": "status.layeredwaterbalance.rates.EVW"},
                "EVS": {"Description": "Actual evaporation rate from soil",
                        "Type": "Number", "UnitOfMeasure": "cm",
                        "StatusVariable": "status.layeredwaterbalance.rates.EVS"},
              
                "RINPRE": {"Description": "Preliminary infiltration rate",
                           "Type": "Number", "UnitOfMeasure": "cm",
                           "StatusVariable": "status.layeredwaterbalance.rates.RINPRE"},
                "RIN": {"Description": "Infiltration rate",
                        "Type": "Number", "UnitOfMeasure": "cm",
                        "StatusVariable": "status.layeredwaterbalance.rates.RIN"},
                "BOTTOMFLOW": {"Description": "Flow rate at the bottom of the profile",
                               "Type": "Number", "UnitOfMeasure": "cm",
                               "StatusVariable": "status.layeredwaterbalance.rates.BOTTOMFLOW"},
                "DSS": {"Description": "Rate of change of surface storage",
                        "Type": "Number", "UnitOfMeasure": "cm",
                        "StatusVariable": "status.layeredwaterbalance.rates.DSS"},
                "DTSR": {"Description": "Rate of change of surface runoff",
                         "Type": "Number", "UnitOfMeasure": "cm",
                         "StatusVariable": "status.layeredwaterbalance.rates.DTSR"},
                "DRAINT": {"Description": "Incoming rainfall rate",
                           "Type": "Number", "UnitOfMeasure": "",
                           "StatusVariable": "status.layeredwaterbalance.rates.DRAINT"},
                "RINold": {"Description": "Previous infiltration rate",
                           "Type": "Number", "UnitOfMeasure": "cm",
                           "StatusVariable": "status.layeredwaterbalance.states.RINold"},
                "WC": {"Description": "Water content in soil layers",
                       "Type": "Number", "UnitOfMeasure": "cm",
                       "StatusVariable": "status.layeredwaterbalance.parameters.SOIL_LAYERS[].WC"},
                "SM": {"Description": "Soil moisture content in soil layers",
                       "Type": "Number", "UnitOfMeasure": "",
                       "StatusVariable": "status.layeredwaterbalance.parameters.SOIL_LAYERS[].SM"},
                "RSM": {"Description": "Relative soil moisture in soil layers",
                        "Type": "Number", "UnitOfMeasure": "unitless",
                        "StatusVariable": "status.layeredwaterbalance.parameters.SOIL_LAYERS[].RSM"},
                "WTRAP": {"Description": "Total potential transpiration",
                          "Type": "Number", "UnitOfMeasure": "cm",
                          "StatusVariable": "status.layeredwaterbalance.states.WTRAP"},
                "WTRAT": {"Description": "Total actual crop transpiration",
                          "Type": "Number", "UnitOfMeasure": "cm",
                          "StatusVariable": "status.layeredwaterbalance.states.WTRAT"},
                "EVWT": {"Description": "Total evaporation from surface water layer and/or soil",
                         "Type": "Number", "UnitOfMeasure": "cm",
                         "StatusVariable": "status.layeredwaterbalance.states.EVWT"},
                "EVST": {"Description": "Total evaporation from surface water layer and/or soil (different from EVWT)",
                         "Type": "Number", "UnitOfMeasure": "cm",
                         "StatusVariable": "status.layeredwaterbalance.states.EVST"},
                "RAINT": {"Description": "Total rainfall",
                          "Type": "Number", "UnitOfMeasure": "cm",
                          "StatusVariable": "status.layeredwaterbalance.states.RAINT"},
                "TOTINF": {"Description": "Total infiltration",
                           "Type": "Number", "UnitOfMeasure": "cm",
                           "StatusVariable": "status.layeredwaterbalance.states.TOTINF"},
                "TOTIRR": {"Description": "Total irrigation",
                           "Type": "Number", "UnitOfMeasure": "cm",
                           "StatusVariable": "status.layeredwaterbalance.states.TOTIRR"},
                "SS": {"Description": "Total surface storage",
                       "Type": "Number", "UnitOfMeasure": "cm",
                       "StatusVariable": "status.layeredwaterbalance.states.SS"},
                "TSR": {"Description": "Total surface runoff",
                        "Type": "Number", "UnitOfMeasure": "cm",
                        "StatusVariable": "status.layeredwaterbalance.states.TSR"},
                "BOTTOMFLOWT": {"Description": "Total outflow through the bottom of the profile",
                                "Type": "Number", "UnitOfMeasure": "cm",
                                "StatusVariable": "status.layeredwaterbalance.states.BOTTOMFLOWT"},
                "LOSST": {"Description": "Loss to subsoil",
                          "Type": "Number", "UnitOfMeasure": "cm",
                          "StatusVariable": "status.layeredwaterbalance.states.LOSST"},
                "CRT": {"Description": "Percolation from the root zone",
                        "Type": "Number", "UnitOfMeasure": "",
                        "StatusVariable": "status.layeredwaterbalance.states.CRT"},
                "W": {"Description": "Total water in the rooted zone",
                      "Type": "Number", "UnitOfMeasure": "cm",
                      "StatusVariable": "status.layeredwaterbalance.states.W"},
                "WLOW": {"Description": "Total water in the potentially rooted zone",
                         "Type": "Number", "UnitOfMeasure": "cm",
                         "StatusVariable": "status.layeredwaterbalance.states.WLOW"},
                "WWLOW": {"Description": "Total water in the rooted and potentially rooted zones",
                          "Type": "Number", "UnitOfMeasure": "cm",
                          "StatusVariable": "status.layeredwaterbalance.states.WWLOW"},
                "WBOT": {"Description": "Total water in the unrooted zone",
                         "Type": "Number", "UnitOfMeasure": "cm",
                         "StatusVariable": "status.layeredwaterbalance.states.WBOT"},
                "WAVUPP": {"Description": "Total available water in the rooted zone",
                           "Type": "Number", "UnitOfMeasure": "cm",
                           "StatusVariable": "status.layeredwaterbalance.states.WAVUPP"},
                "WAVLOW": {"Description": "Total available water in the potentially rooted zone",
                           "Type": "Number", "UnitOfMeasure": "cm",
                           "StatusVariable": "status.layeredwaterbalance.states.WAVLOW"},
                "WAVBOT": {"Description": "Total available water in the unrooted zone",
                           "Type": "Number", "UnitOfMeasure": "cm",
                           "StatusVariable": "status.layeredwaterbalance.states.WAVBOT"},
                "SM_MEAN": {"Description": "Average soil moisture in the rooted zone",
                            "Type": "Number", "UnitOfMeasure": "",
                            "StatusVariable": "status.layeredwaterbalance.states.SM_MEAN"},
                "RSM_rooted_zone": {"Description": "Relative soil moisture in the rooted zone",
                                    "Type": "Number", "UnitOfMeasure": "unitless",
                                    "StatusVariable": "status.layeredwaterbalance.states.RSM_rooted_zone"},

            }



        }


