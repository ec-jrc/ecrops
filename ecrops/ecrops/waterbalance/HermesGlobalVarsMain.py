import numpy as np


class HermesGlobalVarsMain:
    """ This class hosts the main variables used by HermesWaterBalance step"""

    N = 0
    """number of soil layers"""

    DRAIDEP = 0
    """drainage depth in [dm]. Fill with “20” if no tile drains are present."""

    DRAIFAK = 0
    """DrainFactor: defines the percentage of water above field capacity which is lost to the drain. Fill with “00” 
    if no tile drains are present """

    DZ = np.zeros(21, dtype=float)
    """thickness of layers (cm)"""

    IZM = 0
    """soil specific depth for mineralisation (sand > clay)"""

    LBLS = np.zeros(21, dtype=float)
    """lower layer depth (cm)"""

    Q1 = np.zeros(21, dtype=float)
    """ water flux through the bottom of layer (cm/d)"""

    TP = np.zeros(21, dtype=float)

    TD = np.zeros(21, dtype=float)
    """layer temperature (C)"""

    WG = np.zeros((2, 21), dtype=float)
    """water content of layer (cm^3/cm^3)"""

    WNOR = np.zeros((2, 21), dtype=float)
    """NORM-field capacity (without water logging) in layer Z (cm^3/cm^3)"""

    WMIN = np.zeros(21, dtype=float)
    """Wilting point of layers (cm^3/cm^3)"""

    PORGES = np.zeros(21, dtype=float)
    """Total pore space in layer (cm^3/cm^3)"""

    W = np.zeros(21, dtype=float)
    """Field capacity of layer (cm^3/cm^3)"""
