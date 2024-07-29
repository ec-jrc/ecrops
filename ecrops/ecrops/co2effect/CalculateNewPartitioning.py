from ecrops.Step import Step
from ..Printable import Printable

class CalculateNewPartitioning(Step):
    """Class for recalculate the partitioning coefficients using CO2 data.

    =======  ============================================= =======  ============
    Name     Description                                   Type     Unit
    =======  ============================================= =======  ============
    FR       Partitioning to roots as a function of          TCr       -
             development stage.
    FS       Partitioning to stems as a function of          TCr       -
             development stage.
    FL       Partitioning to leaves as a function of         TCr       -
             development stage.
    FO       Partitioning to storage organs as a function    TCr       -
             of development stage.
    =======  ============================================= =======  ============

    Name     Description                         Pbl                Unit
    =======  =================================== =================  ============
    GRLV     Growth rate leaves                   N                 kg ha-1 d-1
    =======  =================================== =================  ============

    """

    def getparameterslist(self):
        return {
            "CVL": {"Description": "Conversion factor for assimilates to leaves", "Type": "Number", "Mandatory": "True",
                    "UnitOfMeasure": "unitless"},
            "CVR": {"Description": "Conversion factor for assimilates to roots", "Type": "Number", "Mandatory": "True",
                    "UnitOfMeasure": "unitless"},
            "CVO": {"Description": "Conversion factor for assimilates to storage organs", "Type": "Number", "Mandatory": "True",
                    "UnitOfMeasure": "unitless"},
            "CVS": {"Description": "Conversion factor for assimilates to stems", "Type": "Number", "Mandatory": "True",
                    "UnitOfMeasure": "unitless"}

        }

    def setparameters(self,status):
        # make a copy of actual partitioning coefficients
        return status

    def runstep(self,status):

        # execute only after emergence and before maturity
        if (status.states.DOE is None or status.day < status.states.DOE) or ( status.states.DOE is not None and status.day >= status.states.DOE and (status.states.DOM is not None and  status.day >= status.states.DOM)):  # execute only after emergence and before maturity
            return status

        # total biomass without co2
        totalBiomassNoCo2 = status.co2data.DMI_NoCo2

        # leaves biomass CO2 Case
        cropASRCAfterCO2 =  status.rates.ASRC


        # parameters retrieved from DVS_Partioniong and Wofost_GrowthRepiration
        FR = status.states.FR
        FL = status.states.FL
        FS = status.states.FS
        FO = status.states.FO
        CVL = status.growthrespiration.params.CVL
        CVR = status.growthrespiration.params.CVR
        CVO = status.growthrespiration.params.CVO
        CVS = status.growthrespiration.params.CVS

        # constant of increment roots
        deltaco2 = status.Co2Concentration - status.Co2FertReference
        alfa = 0.085
        constRoot = 1 + alfa * deltaco2 / 100

        beta = 0.1
        MS = totalBiomassNoCo2 * (1 - FR) * FL
        MT = MS *(1+beta*deltaco2/100)




        if totalBiomassNoCo2 > 0 and cropASRCAfterCO2 > 0:

            if FR != 0:
                FR = 1 / (1 + ((1 - FR) / (constRoot * FR)))

            #Z = (totalBiomassNoCo2 * (1 - status.states.FR) * FL) / cropASRCAfterCO2 * (1 - FR)

            #FL=(-1/CVS +FO/CVS - FO/CVO +FR/CVS-FO*FR/CVS-FR*FO/CVO-FR/CVR)/(-1/CVS + 1/CVL + FR/CVS + FR/CVL - 1/Z)

            H=totalBiomassNoCo2*(1-status.states.FR)*status.states.FL
            MR = (H / cropASRCAfterCO2) * 1 / (1 - FR) * FR / CVR

            FL = ((H / cropASRCAfterCO2) * ((1 - FO) / CVS + FO / CVO) + MR) / (
            1 - (H / cropASRCAfterCO2) * (CVS - CVL) / (CVS * CVL))




            # FL= ((-CVL*CVO+FO*(CVS*CVL-CVL*CVO))*(1-FR)/(CVS*CVL*CVO) + FR/CVR)/\
            #     (cropASRCAfterCO2*(1-FR)/MT - ((CVS*CVO-CVL*CVO)*(1-FR)/(CVS*CVL*CVO)))

            FS = 1 - FO - FL

        # save parameters for a new partioning run
        status.states.FR = FR
        status.states.FL = FL
        status.states.FS = FS

        #print('status.states.FL=' + str(status.states.FL))
        return status

    def initialize(self,status):
        return status

    def integrate(self,status):
        return status

    def getinputslist(self):
        return {

            "FR": {"Description": "Partitioning to roots", "Type": "Number", "UnitOfMeasure": "unitless",
                   "StatusVariable": "status.states.FR"},
            "FL": {"Description": "Partitioning to leaves", "Type": "Number", "UnitOfMeasure": "unitless",
                   "StatusVariable": "status.states.FL"},
            "FS": {"Description": "Partitioning to stems", "Type": "Number", "UnitOfMeasure": "unitless",
                   "StatusVariable": "status.states.FS"},
            "FO": {"Description": "Partitioning to storage organs", "Type": "Number", "UnitOfMeasure": "unitless",
                   "StatusVariable": "status.states.FO"},
            "Co2Concentration": {"Description": "Co2 concentration",
                                 "Type": "Number", "UnitOfMeasure": "ppm",
                                 "StatusVariable": "status.Co2Concentration"},
            "Co2FertReference": {"Description": "Co2 reference",
                                 "Type": "Number", "UnitOfMeasure": "ppm",
                                 "StatusVariable": "status.Co2FertReference"},
            "DMI_NoCo2": {"Description": "Daily increase of total dry matter", "Type": "Number",
                          "UnitOfMeasure": "unitless",
                          "StatusVariable": "status.co2data.DMI_NoCo2"},
            "ASRC": {"Description": "Available respiration", "Type": "Number", "UnitOfMeasure": " kg CH2O kg-1",
                     "StatusVariable": "status.rates.ASRC"},
            "day": {"Description": "Current day", "Type": "Number", "UnitOfMeasure": "doy",
                    "StatusVariable": "status.day"},
            "DOM": {"Description": "Doy of maturity", "Type": "Number", "UnitOfMeasure": "doy",
                    "StatusVariable": "status.states.DOM"},
            "DOE": {"Description": "Doy of emergence", "Type": "Number", "UnitOfMeasure": "doy",
                    "StatusVariable": "status.states.DOE"},
        }

    def getoutputslist(self):
        return {
            "FR": {"Description": "Partitioning to roots", "Type": "Number", "UnitOfMeasure": "unitless",
                   "StatusVariable": "status.states.FR"},
            "FL": {"Description": "Partitioning to leaves", "Type": "Number", "UnitOfMeasure": "unitless",
                   "StatusVariable": "status.states.FL"},
            "FS": {"Description": "Partitioning to stems", "Type": "Number", "UnitOfMeasure": "unitless",
                   "StatusVariable": "status.states.FS"},
            "FO": {"Description": "Partitioning to storage organs", "Type": "Number", "UnitOfMeasure": "unitless",
                   "StatusVariable": "status.states.FO"},

        }