import math
from datetime import timedelta

import ecrops.wofost_util.Afgen
from ..Printable import Printable
from ecrops.Step import Step

class KernelMaize_Otegui_Gambin(Step):
    """
    Kernel Maize using Otegui & Gambin logics, in this version the period to consider after flowering is based on number of days

    Implementation of Otegui & Gambin logics relative to yield estimation for maize

    Simulation parameters* (provide in cropdata dictionary)

    FORMAL PARAMETERS:  (I=input,O=output,C=control,IN=init,T=time)

    =======         ================================================= ==== ============
     Name           Description                                       Pbl      Unit
    =======         ================================================= ==== ============
    KDIF            Extinction coefficient for diffuse light            N   -
    TBASEM          temperature base                                    N   -
    PLD             Plant density                                       N   plant/m-2
    =======         ================================================= ==== ============

    States variables
    =======         ================================================= ==== ============
     Name           Description                                       Pbl      Unit
    =======         ================================================= ==== ============
    TAGP            Total        above - ground                        N    kg/ha - 1
    LAI             Leaf area index                                    N    ha/ha
    IRRAD           Daily shortwave radiation                          N    J m-2 d-1
    KDIF            Extinction coefficient for diffuse light           N    -
    =======         ================================================= ==== ============

    Kernel variables
    =============   ================================================= ==== ============
     Name           Description                                       Pbl      Unit
    =============   ================================================= ==== ============
    YLDES           Yield estimation                                   N    kg/ha
    KernelNumber    Kernel number                                      N    -
    KernelWeight    Kernel weight                                      N    mg
    =============   ================================================= ==== ============


    """

    def getparameterslist(self):
        return {
            "DTSMTB": {"Description": "Daily increase in temperature sum as a function of daily mean temperature.",
                       "Type": "Number",
                       "Mandatory": "True",
                       "UnitOfMeasure": "C"},
            "PlantDensity": {"Description": "Plant density per square meter", "Type": "Number",
                             "Mandatory": "True",
                             "UnitOfMeasure": "unitless"}
        }

    def getinputslist(self):
        return {
            # to be implemented
        }

    def getoutputslist(self):
        return {
            # to be implemented
        }
    def setparameters(self, status):
        """
        Set the parameters used inside the Wofost process for the Otegui-Gambin algorithm
        """
        status.kernel = Printable()
        status.kernel.PlantDensity = status.allparameters[
            'PlantDensity']  # plant density for m2 (old value hardcoded: 8
        status.kernel.DOAGrade = None  # Day grade for the day of anthesys (flowering day)
        status.kernel.DaysGradeCum = 0
        status.kernel.TBASE = ecrops.wofost_util.Afgen.Afgen(status.allparameters['DTSMTB']).x_list[1]
        return status

    def initialize(self, status):
        """
        Initialize the list of days grade and IPAR values
        """
        status.kernel.DaysGrade = list()  # day grade for all days until the calculation of yield estimation moment
        status.kernel.DaysIPAR = list()  # list to store all IPAR values untill of yield estimation moment
        status.kernel.AllTAGP = list()  # store all TAGP values
        status.kernel.KernelIPAR = 0  # sum of daily IPAR values for the interval of days for which we have -227 : 100 day grades relative to value cumulated on DOA
        status.kernel.KernelNumber = None
        status.kernel.KernelWeight = None
        status.kernel.LeavesBiomassAtFlowering = None
        status.kernel.StemsBiomassAtFlowering = None
        status.kernel.TotalBiomassAtFlowering = None
        status.kernel.YLDES = None  # yield estimation
        status.kernel.YLDES_AfterGrainFilling = 0  # yield estimation after grain filling period
        status.kernel.KernelWeight_AfterGrainFilling = None  # kernel weigth after grain filling
        status.kernel.YLDES_AfterGrainFilling_WithTranslocation = 0  # yield estimation after grain filling period considering translocation
        status.kernel.KernelWeight_AfterGrainFilling_WithTranslocation = None  # kernel weigth after grain filling considering translocation
        status.kernel.dailySO_BiomassRates = []
        status.kernel.dailyDTSUMs = []
        return status

    def integrate(self, status):
        """
        - for all days calculate day grade and IPAR

        - for DOA (flowering day) save the value of day grade

        - for all days great than DOA and if yield estimation was not calculated than try to identify the interval of
        [-227:100] days grade and [-15:15] of IPAR
        """
        # if the estimation was done or there is no crop return
        if (status.kernel.KernelWeight_AfterGrainFilling is not None or status.states.DVS == 0):
            return status

        # add TAGP value to the list
        status.kernel.AllTAGP.append(status.states.TAGP)

        # DOA
        DOA = status.states.DOA

        # save the dayGrade as DOAGrade. Calculate the total of IPAR values for all days until -227 days grade relative to cumulated value of DOA
        if DOA is not None and DOA == status.day - timedelta(days=1):
            status.kernel.DOAGrade = status.kernel.DaysGradeCum

            # calculate the sum of daily IPAR values , backward, until the difference of DayGradeDOA and daily values >= -227
            tmpCumDaysGrade = 0
            iparIndex = len(status.kernel.DaysIPAR) - 1
            while (tmpCumDaysGrade <= 227 and iparIndex >= 0):
                tmpCumDaysGrade = tmpCumDaysGrade + status.kernel.DaysGrade[iparIndex]
                status.kernel.KernelIPAR = status.kernel.KernelIPAR + status.kernel.DaysIPAR[iparIndex]
                iparIndex = iparIndex - 1

        # calculate the day grade
        dayGrade = (status.weather.TEMP_MAX + status.weather.TEMP_MIN) / 2 - status.kernel.TBASE
        status.kernel.DaysGrade.append(dayGrade)
        status.kernel.DaysGradeCum = status.kernel.DaysGradeCum + dayGrade

        # calculate IPAR for plant (IRRAD expressed in MJ)
        dayIPAR = (status.weather.IRRAD / 1000000 * 0.45) * (
                1 - math.exp(-1 * status.states.KDIF * status.states.LAI)) / status.kernel.PlantDensity
        status.kernel.DaysIPAR.append(dayIPAR)

        # add IPAR values to the KernelIPAR total for the days untill the difference of daysgrade relative to DOA are >= 100
        if DOA is not None and status.day > DOA \
                and status.kernel.DaysGradeCum - status.kernel.DOAGrade <= 100:
            status.kernel.KernelIPAR = status.kernel.KernelIPAR + dayIPAR

        # calculate KernelNumber when the difference od days grade is > 100
        if DOA is not None \
                and status.kernel.KernelNumber is None \
                and status.kernel.DaysGradeCum - status.kernel.DOAGrade > 100:
            status.kernel.KernelIPAR = status.kernel.KernelIPAR + dayIPAR
            status.kernel.KernelNumber = status.kernel.PlantDensity * (97 + 15 * status.kernel.KernelIPAR)

        # check if the current day is 15 days after DOA and then calculate the Kernel weight
        if (DOA is not None and status.day == DOA + timedelta(days=16)):
            # calculate the biomass increment
            daysCounter = len(status.kernel.AllTAGP)
            biomassIncrement = status.kernel.AllTAGP[daysCounter - 1] - status.kernel.AllTAGP[daysCounter - 31]

            # calculate the sum of days grade on the same interval
            totalDaysGrade = 0
            indexDaysGrade = len(status.kernel.DaysGrade)
            for i in range(1, 31):
                totalDaysGrade = totalDaysGrade + status.kernel.DaysGrade[indexDaysGrade - i]
                i = i + 1

            plantGrowthRateAroundFlowering = biomassIncrement * (
                        1000000 / (10000 * status.kernel.PlantDensity)) / totalDaysGrade

            # davide: 04/05/2020 changed the equations. NEW ONES:
            PlantGrowthRatePerKernelAroundFlowering = 0.0007 * plantGrowthRateAroundFlowering + 0.3773
            status.kernel.KernelWeight = - 8.7108 + 522.24 * PlantGrowthRatePerKernelAroundFlowering  # mg

            # davide: 04/05/2020 changed the equations. OLD ONES:
            # PlantGrowthRatePerKernelAroundFlowering=0.00176 * plantGrowthRateAroundFlowering + 0.023
            # status.kernel.KernelWeight = 233 + 177 * PlantGrowthRatePerKernelAroundFlowering #mg

        # calculate yield estimation if both kernel values are already computed
        if (status.kernel.KernelWeight is not None and status.kernel.KernelNumber is not None):
            status.kernel.YLDES = 1000 * status.kernel.KernelNumber * status.kernel.KernelWeight / 100000;  # kg/ha

        # if there is partitioning to the storage organs
        if status.states.DVS >= 1 and status.kernel.LeavesBiomassAtFlowering == None:
            status.kernel.LeavesBiomassAtFlowering = status.states.TWLV
            status.kernel.StemsBiomassAtFlowering = status.states.TWST
            status.kernel.TotalBiomassAtFlowering = status.states.TAGP

        if status.states.DVS >= 1 and status.states.DVS < 2:
            status.kernel.dailySO_BiomassRates.append(status.rates.GRSO)
            status.kernel.dailyDTSUMs.append(status.rates.DTSUM)

        if status.states.DVS >= 2:

            DELTA_GDD = 200

            # calculate the potential graing growth rate per degree day as the yield calculated by outegui-gambin divided by TSUM2
            potentialGrainGrowthRateGDD = status.kernel.YLDES / (status.phenology.params.TSUM2 - DELTA_GDD)

            cumGDD = 0
            for i in range(0, len(status.kernel.dailySO_BiomassRates)):

                # get the daily storage organs biomass as calculated by wofost
                dailySO_BiomassRate = status.kernel.dailySO_BiomassRates[i]
                dailyGDD = status.kernel.dailyDTSUMs[i]
                cumGDD += dailyGDD

                if cumGDD > DELTA_GDD:
                    # calculate the actual daily graing growth rate per degree day as the daily storage organs biomass rate divided by the daily increase of TSUMs
                    if dailyGDD == 0:
                        dailyGDD = 1  # avoid division by zero
                    actualGrainGrowthRateGDD = dailySO_BiomassRate / dailyGDD

                    if actualGrainGrowthRateGDD < potentialGrainGrowthRateGDD:
                        status.kernel.YLDES_AfterGrainFilling += actualGrainGrowthRateGDD * dailyGDD
                    else:
                        status.kernel.YLDES_AfterGrainFilling += potentialGrainGrowthRateGDD * dailyGDD

            status.kernel.YLDES_AfterGrainFilling = status.kernel.YLDES_AfterGrainFilling * 1.039  # before GDD 200 we estimate we allocate 3.9% of final yield
            status.kernel.YLDES_AfterGrainFilling_WithTranslocation = min(
                status.kernel.YLDES_AfterGrainFilling * 1.039 + 0.15 * status.kernel.LeavesBiomassAtFlowering + 0.20 * status.kernel.StemsBiomassAtFlowering,
                status.kernel.YLDES)  # translocation add some part of leaves and stems biomass to final yield
            status.kernel.KernelWeight_AfterGrainFilling = 100 * status.kernel.YLDES_AfterGrainFilling / status.kernel.KernelNumber
            status.kernel.KernelWeight_AfterGrainFilling_WithTranslocation = 100 * status.kernel.YLDES_AfterGrainFilling_WithTranslocation / status.kernel.KernelNumber

        return status


    def runstep(self, status):

        return status
