class Layer:
    """This class represents a soil layer used in the LayeredWaterBalance and in the nitrogen related steps"""

    SOIL_GROUP_NO = int(-99)
    """soil typology code, used only to check whether soil layers have the same soil type"""

    TSL = float(-99.)
    """Layer thickness [cm]"""

    LBSL = 0  # lower boundary
    """Lower boundary of the layer [cm]"""

    SMFCF = float(-99.)
    """Field capacity point of the layer"""

    SM0 = float(-99.)
    """Porosity (water content at saturation) of the layer"""

    SMW = float(-99.)
    """Wilting point of the layer"""

    WC0 = float(-99.)
    """Water content at saturation (SM0 * thickness) of the layer """

    WCW = float(-99.)
    """Water content at wilting point (SMW * thickness) of the layer"""

    WCFC = float(-99.)
    """Water content  at field capacity  (SMFCF * thickness) of the layer"""

    SOPE = float(-99.)
    """maximum percolation rate root zone [cm day-1]"""

    KSUB = float(-99.)
    """maximum percolation rate subsoil [cm day-1]"""

    K0 = float(-99.)
    """hydraulic conductivity of saturated soil [cm day-1]"""

    CONTAB = None
    """Conductivity from Potential Flux, 10-log hydraulic conductivity as a function of pF (log(cm) log(cm /day) )."""

    SMTAB = None
    """Soil Moisture from Potential Flux, volumetric moisture content as function of (log (cm); cm3/cm3)"""

    PFTAB = None
    """Potential Flux from Soil Moisture, reverse of the SMTAB (X changed with Y, then reordered by X values)"""

    MFPTAB = None
    """Matric Flux Potential. The MFP is defined as the integral of the conductivity K(teta) from -Infinity to a certain teta (teta is the soil moisture content SM).
    The MPF is calculated as an integral of (K(teta) * 10^(pF) * eLog10) over the pF range considered."""

    WaterFromHeight = None
    """Only used for GroundWater: cumulative amount of water as a function of height above groundwater under 
    equilibrium conditions. """

    HeightFromAir = None
    """Only used for GroundWater:  soil air volume above watertable at equilibrium"""

    CRAIRC = None
    """ Critical air content for root aeration"""



    # layer weight factors
    Wtop = float(-99.)
    """layer weight factor Wtop (weights for contribution to rootzone: changes from 0 to 1. 1 means the layer is entirely within the rooted zone. O 
    entirely outside the rooted zone) """

    Wpot = float(-99.)
    """layer weight factor Wpot (weights for contribution to potentially rooted zone) """

    Wund = float(-99.)
    """layer weight factor Wund (weights for contribution to never rooted layers) """

    WC = float(-99.)
    """Actual water content of the layer"""

    CondFC = float(-99.)
    CondK0 = float(-99.)

    SM = float(-99.)
    """Actual soil moisture"""

    DWC = float(-99.)
    """Actual layer water daily change"""

    DownwardFLOWAtBottomOfLayer = 0
    """Downward flow at the bottom of the layer"""
