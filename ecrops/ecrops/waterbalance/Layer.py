from ecrops.wofost_util.Afgen import Afgen


class Layer:
    """This class represents a soil layer used in the LayeredWaterBalance and in the nitrogen related steps"""

    SOIL_GROUP_NO = ""
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


    def __init__(self):
        self.SOIL_GROUP_NO = ""
        self.TSL = float(-99.)
        self.LBSL = 0
        self.SMFCF = float(-99.)
        self.SM0 = float(-99.)
        self.SMW = float(-99.)
        self.WC0 = float(-99.)
        self.WCW = float(-99.)
        self.WCFC = float(-99.)
        self.SOPE = float(-99.)
        self.KSUB = float(-99.)
        self.K0 = float(-99.)
        self.CONTAB = None
        self.SMTAB = None
        self.PFTAB = None
        self.MFPTAB = None
        self.WaterFromHeight = None
        self.HeightFromAir = None
        self.CRAIRC = None
        self.Wtop = float(-99.)
        self.Wpot = float(-99.)
        self.Wund = float(-99.)
        self.WC = float(-99.)
        self.CondFC = float(-99.)
        self.CondK0 = float(-99.)
        self.SM = float(-99.)
        self.DWC = float(-99.)
        self.DownwardFLOWAtBottomOfLayer = 0

    def __init__(self, SOIL_GROUP_NO="", TSL=-99.0, LBSL=0, SMFCF=-99.0, SM0=-99.0, SMW=-99.0, WC0=-99.0, WCW=-99.0, WCFC=-99.0, SOPE=-99.0, KSUB=-99.0, K0=-99.0, CONTAB=None, SMTAB=None, PFTAB=None, MFPTAB=None, WaterFromHeight=None, HeightFromAir=None, CRAIRC=None, Wtop=-99.0, Wpot=-99.0, Wund=-99.0, WC=-99.0, CondFC=-99.0, CondK0=-99.0, SM=-99.0, DWC=-99.0, DownwardFLOWAtBottomOfLayer=0):
        self.SOIL_GROUP_NO = SOIL_GROUP_NO
        self.TSL = TSL
        self.LBSL = LBSL
        self.SMFCF = SMFCF
        self.SM0 = SM0
        self.SMW = SMW
        self.WC0 = WC0
        self.WCW = WCW
        self.WCFC = WCFC
        self.SOPE = SOPE
        self.KSUB = KSUB
        self.K0 = K0
        self.CONTAB = CONTAB
        self.SMTAB = SMTAB
        self.PFTAB = PFTAB
        self.MFPTAB = MFPTAB
        self.WaterFromHeight = WaterFromHeight
        self.HeightFromAir = HeightFromAir
        self.CRAIRC = CRAIRC
        self.Wtop = Wtop
        self.Wpot = Wpot
        self.Wund = Wund
        self.WC = WC
        self.CondFC = CondFC
        self.CondK0 = CondK0
        self.SM = SM
        self.DWC = DWC
        self.DownwardFLOWAtBottomOfLayer = DownwardFLOWAtBottomOfLayer

    def __str__(self):
        return f"Layer('{self.SOIL_GROUP_NO}',{self.TSL},{self.LBSL},{self.SMFCF},{self.SM0},{self.SMW},{self.WC0},{self.WCW},{self.WCFC},{self.SOPE},{self.KSUB},{self.K0},{self.CONTAB},{self.SMTAB},{self.PFTAB},{self.MFPTAB},{self.WaterFromHeight},{self.HeightFromAir},{self.CRAIRC},{self.Wtop},{self.Wpot},{self.Wund},{self.WC},{self.CondFC},{self.CondK0},{self.SM},{self.DWC},{self.DownwardFLOWAtBottomOfLayer})"


if __name__ == '__main__':
    layer = Layer()
    layer.CONTAB = Afgen([1,2,3,4])
    print(str(layer))

    layer2= Layer()
    layer.CONTAB = Afgen([5, 6, 7, 8])

    layers=[layer,layer2]
    print(layers)
