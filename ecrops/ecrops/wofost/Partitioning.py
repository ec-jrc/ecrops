# Template for namedtuple containing partitioning factors
from collections import namedtuple

import ecrops.wofost_util.Afgen
from ..Printable import Printable


class PartioningFactors(namedtuple("partitioning_factors", "FR FL FS FO")):
    """Tuple containing the 4 partitioning factors: FR FL FS FO """
    pass


class DVS_Partitioning:
    """Class for assimilate partitioning based on development stage (`DVS`).

    `DVS_partitioning` calculates the partitioning of the assimilates to roots,
    stems, leaves and storage organs using fixed partitioning tables as a
    function of crop development stage. The available assimilates are first
    split into below-ground and abovegrond using the values in FRTB. In a
    second stage they are split into leaves (`FLTB`), stems (`FSTB`) and storage
    organs (`FOTB`).

    Since the partitioning fractions are derived from the state variable `DVS`
    they are regarded state variables as well.

    **Simulation parameters** (To be provided in cropdata dictionary):

    =======  ============================================= =======  ============
     Name     Description                                   Type     Unit
    =======  ============================================= =======  ============
    FRTB     Partitioning to roots as a function of          TCr       -
             development stage.
    FSTB     Partitioning to stems as a function of          TCr       -
             development stage.
    FLTB     Partitioning to leaves as a function of         TCr       -
             development stage.
    FOTB     Partitioning to storage organs as a function    TCr       -
             of development stage.
    =======  ============================================= =======  ============


    **State variables**

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    FR        Fraction partitioned to roots.                     Y    -
    FS        Fraction partitioned to stems.                     Y    -
    FL        Fraction partitioned to leaves.                    Y    -
    FO        Fraction partitioned to storage orgains            Y    -
    =======  ================================================= ==== ============

    **Rate variables**

    None

    **Signals send or handled**

    None

    **External dependencies:**

    =======  =================================== =================  ============
     Name     Description                         Provided by         Unit
    =======  =================================== =================  ============
    DVS      Crop development stage              DVS_Phenology       -
    =======  =================================== =================  ============

    *Exceptions raised*

    A PartitioningError is raised if the partitioning coefficients to leaves,
    stems and storage organs on a given day do not add up to '1'.
    """

    def getparameterslist(self):
        return {
            "FRTB": {"Description": "Fraction partitioned to roots", "Type": "Number",
                     "Mandatory": "True", "UnitOfMeasure": "unitless"},
            "FLTB": {"Description": "Fraction partitioned to leaves", "Type": "Number",
                     "Mandatory": "True", "UnitOfMeasure": "unitless"},
            "FSTB": {"Description": "Fraction partitioned to stems", "Type": "Number",
                     "Mandatory": "True", "UnitOfMeasure": "unitless"},
            "FOTB": {"Description": "Fraction partitioned to storage organs", "Type": "Number",
                     "Mandatory": "True", "UnitOfMeasure": "unitless"},
        }

    def setparameters(self, status):
        status.partitioning = Printable()
        status.partitioning.params = Printable()
        cropparams = status.allparameters
        status.partitioning.params.FRTB = ecrops.wofost_util.Afgen.Afgen(cropparams['FRTB'])
        status.partitioning.params.FLTB = ecrops.wofost_util.Afgen.Afgen(cropparams['FLTB'])
        status.partitioning.params.FSTB = ecrops.wofost_util.Afgen.Afgen(cropparams['FSTB'])
        status.partitioning.params.FOTB = ecrops.wofost_util.Afgen.Afgen(cropparams['FOTB'])
        return status

    # FRTB = Afgen.Afgen(
    #     [0, 0.4, 0.1, 0.37, 0.2, 0.34, 0.3, 0.31, 0.4, 0.27, 0.5, 0.23, 0.6, 0.19, 0.7, 0.15, 0.8, 0.1, 0.9, 0.06, 1, 0,
    #      2, 0])
    # FLTB = Afgen.Afgen([0, 0.62, 0.33, 0.62, 0.88, 0.15, 0.95, 0.15, 1.1, 0.1, 1.2, 0, 2, 0])
    # FSTB = Afgen.Afgen([0, 0.38, 0.33, 0.38, 0.88, 0.85, 0.95, 0.85, 1.1, 0.4, 1.2, 0, 2, 0])
    # FOTB = Afgen.Afgen([0, 0, 0.33, 0, 0.88, 0, 0.95, 0, 1.1, 0.5, 1.2, 1, 2, 1])

    def initialize(self, status):

        status = self.runstep(status)

        return status

    def _check_partitioning(self, s):
        """Check for partitioning errors."""

        FR = s.FR
        FL = s.FL
        FS = s.FS
        FO = s.FO
        checksum = FR + (FL + FS + FO) * (1. - FR) - 1.
        if abs(checksum) >= 0.0001:
            msg = ("Error in partitioning!\n")
            msg += ("Checksum: %f, FR: %5.3f, FL: %5.3f, FS: %5.3f, FO: %5.3f\n" \
                    % (checksum, FR, FL, FS, FO))
            # raise Exception(msg)

    def runstep(self, status):
        """Update partitioning factors based on development stage (DVS)"""

        DVS = status.states.DVS
        status.states.FR = status.partitioning.params.FRTB(DVS)
        status.states.FL = status.partitioning.params.FLTB(DVS)
        status.states.FS = status.partitioning.params.FSTB(DVS)
        status.states.FO = status.partitioning.params.FOTB(DVS)

        # Pack partitioning factors into tuple
        status.states.PF = PartioningFactors(status.states.FR, status.states.FL, status.states.FS, status.states.FO)

        self._check_partitioning(status.states.PF)
        return status

    def integrate(self, status):
        return status
