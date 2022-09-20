from ..Printable import Printable


class WOFOST_Storage_Organ_Dynamics:
    """Implementation of storage organ dynamics.

    Storage organs are the most simple component of the plant in WOFOST and
    consist of a static pool of biomass. Growth of the storage organs is the
    result of assimilate partitioning. Death of storage organs is not
    implemented and the corresponding rate variable (DRSO) is always set to
    zero.

    Pods are green elements of the plant canopy and can as such contribute
    to the total photosynthetic active area. This is expressed as the Pod
    Area Index which is obtained by multiplying pod biomass with a fixed
    Specific Pod Area (SPA).

    **Simulation parameters**

    =======  ============================================= =======  ============
     Name     Description                                   Type     Unit
    =======  ============================================= =======  ============
    TDWI     Initial total crop dry weight                  SCr      |kg ha-1|
    SPA      Specific Pod Area                              SCr      |ha kg-1|
    =======  ============================================= =======  ============

    **State variables**

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    PAI      Pod Area Index                                     Y     -
    WSO      Weight of living storage organs                    Y     |kg ha-1|
    DWSO     Weight of dead storage organs                      N     |kg ha-1|
    TWSO     Total weight of storage organs                     Y     |kg ha-1|
    =======  ================================================= ==== ============

    **Rate variables**

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    GRSO     Growth rate storage organs                         N   |kg ha-1 d-1|
    DRSO     Death rate storage organs                          N   |kg ha-1 d-1|
    GWSO     Net change in storage organ biomass                N   |kg ha-1 d-1|
    =======  ================================================= ==== ============

    **Signals send or handled**

    None

    **External dependencies**

    =======  =================================== =================  ============
     Name     Description                         Provided by         Unit
    =======  =================================== =================  ============
    ADMI     Above-ground dry matter             CropSimulation     |kg ha-1 d-1|
             increase
    FO       Fraction biomass to storage organs  DVS_Partitioning    -
    FR       Fraction biomass to roots           DVS_Partitioning    -
    =======  =================================== =================  ============
    """

    def getparameterslist(self):
        return {
            "SPA": {"Description": "Specific Pod Area", "Type": "Number", "Mandatory": "True",
                    "UnitOfMeasure": "ha kg-1"},
            "TDWI": {"Description": "Initial total crop dry weight", "Type": "Number", "Mandatory": "True",
                     "UnitOfMeasure": "kg ha-1"}
        }

    def setparameters(self, status):
        status.storageorgansdynamics = Printable()
        status.storageorgansdynamics.params = Printable()
        cropparams = status.allparameters
        status.storageorgansdynamics.params.SPA = cropparams['SPA']
        status.storageorgansdynamics.params.TDWI = cropparams['TDWI']
        return status

    def initialize(self, status):
        status.states.WSO = 0.
        status.states.DWSO = 0.
        status.states.TWSO = 0.
        status.states.PAI = 0.

        status.rates.GRSO = 0.
        status.rates.DRSO = 0.0
        status.rates.GWSO = 0.
        status.states.PAI = 0.
        return status

    def runstep(self, status):
        states = status.states
        status.rates.GRSO = 0.
        status.rates.DRSO = 0.0
        status.rates.GWSO = 0.
        if (states.DOE is None or status.day < states.DOE) or (states.DOE is not None and status.day >= states.DOE and (
                states.DOM is not None and status.day >= states.DOM)):  # execute only after emergence and before maturity
            return status

        rates = status.rates

        params = status.storageorgansdynamics.params

        FO = status.states.FO
        ADMI = status.rates.ADMI

        # Growth/death rate organs
        rates.GRSO = ADMI * FO
        rates.DRSO = 0.0
        rates.GWSO = rates.GRSO - rates.DRSO

        return status

    def integrate(self, status):
        rates = status.rates
        states = status.states
        params = status.storageorgansdynamics.params

        # INITIAL STATES at sowing/emergence day
        if status.day == status.states.DOS or status.day == status.states.DOE:
            # Initial storage organ biomass
            FO = status.states.FO
            FR = status.states.FR
            status.states.WSO = (params.TDWI * (1 - FR)) * FO
            status.states.DWSO = 0.
            status.states.TWSO = status.states.WSO + status.states.DWSO
            # Initial Pod Area Index
            status.states.PAI = status.states.WSO * params.SPA

        # Stem biomass (living, dead, total)
        states.WSO += rates.GWSO
        states.DWSO += rates.DRSO
        states.TWSO = states.WSO + states.DWSO

        # Calculate Pod Area Index (SAI)
        states.PAI = states.WSO * params.SPA
        return status
