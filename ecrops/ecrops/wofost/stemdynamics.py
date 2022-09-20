import ecrops.wofost_util.Afgen
from ..Printable import Printable


class WOFOST_Stem_Dynamics:
    """Implementation of stem biomass dynamics.

    Stem biomass increase results from the assimilates partitioned to
    the stem system. Stem death is defined as the current stem biomass
    multiplied by a relative death rate (`RDRSTB`). The latter as a function
    of the development stage (`DVS`).

    Stems are green elements of the plant canopy and can as such contribute
    to the total photosynthetic active area. This is expressed as the Stem
    Area Index which is obtained by multiplying stem biomass with the
    Specific Stem Area (SSATB), which is a function of DVS.

    **Simulation parameters**:

    =======  ============================================= =======  ============
     Name     Description                                   Type     Unit
    =======  ============================================= =======  ============
    TDWI     Initial total crop dry weight                  SCr       |kg ha-1|
    RDRSTB   Relative death rate of stems as a function     TCr       -
             of development stage
    SSATB    Specific Stem Area as a function of            TCr       |ha kg-1|
             development stage
    =======  ============================================= =======  ============


    **State variables**

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    SAI      Stem Area Index                                    Y     -
    WST      Weight of living stems                             Y     |kg ha-1|
    DWST     Weight of dead stems                               N     |kg ha-1|
    TWST     Total weight of stems                              Y     |kg ha-1|
    =======  ================================================= ==== ============

    **Rate variables**

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    GRST     Growth rate stem biomass                           N   |kg ha-1 d-1|
    DRST     Death rate stem biomass                            N   |kg ha-1 d-1|
    GWST     Net change in stem biomass                         N   |kg ha-1 d-1|
    =======  ================================================= ==== ============

    **Signals send or handled**

    None

    **External dependencies:**

    =======  =================================== =================  ============
     Name     Description                         Provided by         Unit
    =======  =================================== =================  ============
    DVS      Crop development stage              DVS_Phenology       -
    ADMI     Above-ground dry matter             CropSimulation     |kg ha-1 d-1|
             increase
    FR       Fraction biomass to roots           DVS_Partitioning    -
    FS       Fraction biomass to stems           DVS_Partitioning    -
    =======  =================================== =================  ============
    """

    def getparameterslist(self):
        return {
            "RDRSTB": {"Description": "Relative death rate of stems as a function of DVS", "Type": "Array",
                       "Mandatory": "True", "UnitOfMeasure": "unitless"},
            "SSATB": {"Description": "Specific Stem Area as a function of DVS", "Type": "Array", "Mandatory": "True",
                      "UnitOfMeasure": "ha kg-1"},
            "TDWI": {"Description": "Initial total crop dry weight", "Type": "Number", "Mandatory": "True",
                     "UnitOfMeasure": "kg ha-1"}
        }

    def setparameters(self, status):
        status.stemdynamics = Printable()
        status.stemdynamics.params = Printable()
        cropparams = status.allparameters
        status.stemdynamics.params.RDRSTB = ecrops.wofost_util.Afgen.Afgen(cropparams['RDRSTB'])
        status.stemdynamics.params.SSATB = ecrops.wofost_util.Afgen.Afgen(cropparams['SSATB'])
        status.stemdynamics.params.TDWI = cropparams['TDWI']
        return status

    def initialize(self, status):

        status.states.WST = 0.
        status.states.DWST = 0.
        status.states.TWST = 0.
        status.states.SAI = 0.
        status.rates.GRST = 0
        status.rates.DRST = 0
        status.rates.GWST = 0
        return status

    def runstep(self, status):
        states = status.states
        status.rates.GRST = 0
        status.rates.DRST = 0
        status.rates.GWST = 0
        if (states.DOE is None or status.day < states.DOE) or (states.DOE is not None and status.day >= states.DOE and (
                states.DOM is not None and status.day >= states.DOM)):  # execute only after emergence and before maturity
            return status

        rates = status.rates
        states = status.states
        params = status.stemdynamics.params

        DVS = status.states.DVS
        FS = status.states.FS
        ADMI = status.rates.ADMI

        # Growth/death rate stems
        rates.GRST = ADMI * FS
        rates.DRST = params.RDRSTB(DVS) * states.WST
        rates.GWST = rates.GRST - rates.DRST

        return status

    def integrate(self, status):
        params = status.stemdynamics.params
        rates = status.rates
        states = status.states

        # INITIAL STATES at sowing/emergence day
        if status.day == status.states.DOS or status.day == status.states.DOE:
            params = status.stemdynamics.params
            # Set initial stem biomass
            FS = status.states.FS
            FR = status.states.FR
            status.states.WST = (params.TDWI * (1 - FR)) * FS
            status.states.DWST = 0.
            status.states.TWST = status.states.WST + status.states.DWST
            # Initial Stem Area Index
            DVS = status.states.DVS
            status.states.SAI = status.states.WST * params.SSATB(DVS)

        # Stem biomass (living, dead, total)
        states.WST += rates.GWST
        states.DWST += rates.DRST
        states.TWST = states.WST + states.DWST

        # Calculate Stem Area Index (SAI)
        DVS = status.states.DVS
        states.SAI = states.WST * params.SSATB(DVS)
        return status
