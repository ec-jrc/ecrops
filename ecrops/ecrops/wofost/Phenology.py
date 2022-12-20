from ecrops.Printable import Printable
import ecrops.wofost_util.Afgen
from ecrops.wofost_util.util import limit


def stopAtMaturity(status,crop):
    """For crops that have END_EVENT=4 (harvest,like crops 6 and 7) returns False, because for some crop we simulate the phenology after maturity. For other
    crops return True """
    if hasattr(status, 'END_EVENT'):
        if status.END_EVENT == 4:
            return False
        else:
            return True
    else:  # NOTE: this case is left for backward compatibility, but should removed because it is always better to explicit the END_EVENT in the driving variables
        return True



class DVS_Phenology:
    """Phenology of Wofost model"""

    def getparameterslist(self):
        return {"IDSL": {
            "Description": "Switch for phenological development options: temperature only (IDSL=0), daylength (IDSL=1) and including vernalization (IDSL>=2)",
            "Type": "Number", "Mandatory": "True", "UnitOfMeasure": "unitless"},
                "TEFFMX": {"Description": "Maximum effective temperature for emergence", "Type": "Number",
                           "Mandatory": "True", "UnitOfMeasure": "C"},
                "TBASEM": {"Description": "Base temperature for emergence", "Type": "Number", "Mandatory": "True",
                           "UnitOfMeasure": "C"},
                "DLC": {"Description": "Critical daylength for phenological development", "Type": "Number",
                        "Mandatory": "True", "UnitOfMeasure": "h"},
                "DLO": {"Description": "Optimal daylength for phenological development", "Type": "Number",
                        "Mandatory": "True", "UnitOfMeasure": "h"},
                "DTSMTB": {"Description": "Daily increase in temperature sum as a function of daily mean temperature",
                           "Type": "Array", "Mandatory": "True", "UnitOfMeasure": "C"},
                "TSUM2": {"Description": "Temperature sum from anthesis to maturity", "Type": "Number",
                          "Mandatory": "True", "UnitOfMeasure": "C day"},
                "DVSEND": {"Description": "Final development stage", "Type": "Number", "Mandatory": "True",
                           "UnitOfMeasure": "unitless"},
                "TSUMEM": {"Description": "Temperature sum from sowing to emergence", "Type": "Number",
                           "Mandatory": "True", "UnitOfMeasure": "C day"}
                }

    def setparameters(self, status):
        try:
            status.phenology = Printable()
            status.phenology.params = Printable()
            cropparams = status.allparameters
            status.phenology.params.IDSL = cropparams['IDSL']
            status.phenology.params.TEFFMX = cropparams['TEFFMX']
            status.phenology.params.TBASEM = cropparams['TBASEM']
            status.phenology.params.DLC = cropparams['DLC']
            status.phenology.params.DLO = cropparams['DLO']
            status.phenology.params.DTSMTB = ecrops.wofost_util.Afgen.Afgen(cropparams['DTSMTB'])
            status.phenology.params.TSUM1 = cropparams['TSUM1']
            status.phenology.params.TSUM2 = cropparams['TSUM2']
            status.phenology.params.TSUMEM = cropparams['TSUMEM']
            status.phenology.params.DVSEND = cropparams['DVSEND']


            if hasattr(status,'START_EVENT'):
                if status.START_EVENT==1:
                    status.phenology.params.CROP_START_TYPE = "sowing"
                else:
                    status.phenology.params.CROP_START_TYPE = "emergence"
                    #if starts at emergence, TSUMEM should be forced to zero
                    cropparams['TSUMEM'] = 0
                    status.phenology.params.TSUMEM = 0
            else: #NOTE: this case is left for backward compatibility, but should removed because it is always better to explicit the START_EVENT in the driving variables
                status.phenology.params.CROP_START_TYPE ="sowing"
        except  Exception as e:
            print('Error in method setparameters of class Phenology:' + str(e))
        return status

    def next_stage(self, status):
        """Moves status.states.STAGE to the next phenological stage"""
        s = status.states

        if s.STAGE == "emerging":
            s.STAGE = "vegetative"
            s.DOE = status.day

        elif s.STAGE == "vegetative":
            s.STAGE = "reproductive"
            s.DOA = status.day

        elif s.STAGE == "reproductive":
            s.STAGE = "mature"
            s.DOM = status.day

        elif s.STAGE == "mature":
            msg = "Cannot move to next phenology stage: maturity already reached!"
            raise Exception(msg)

        else:  # Problem no stage defined
            msg = "No STAGE defined in phenology submodule."
            raise Exception(msg)
        return status

    def initialize(self, status):

        try:

            status.rates.DTSUME = 0
            status.states.TSUME = 0
            status.states.DVS = 0
            status.states.TSUM = 0

            s = status.states
            s.DOS = None
            s.DOE = None
            s.DOA = None
            s.DOM = None
            s.DOV = None
            status.rates.DTSUME = 0.
            status.rates.DTSUM = 0.
            status.rates.DVR = 0.
            status.VERNFAC = 1.  # default (used if there is not vernalization)


        except  Exception as e:
            print('Error in method initialize of class Phenology:' + str(e))

        return status

    def integrate(self, status):
        """Updates the state variable and checks for phenologic stages
        """

        try:
            r = status.rates
            s = status.states



            if s.DOE is None and s.DOS is None: #before sowing and emergence
                return status

            if stopAtMaturity and s.STAGE == 'mature':
                return status

            # Integrate vernalisation module NOTE: moved at the same level of the other components
            # ver = vernalisation()
            # if status.phenology.params.IDSL >= 2:
            #     if s.STAGE == 'vegetative':
            #         status =ver.integrate(status)

            # Integrate phenologic states
            s.TSUME += r.DTSUME
            s.DVS += r.DVR
            s.TSUM += r.DTSUM



            # Check if a new stage is reached
            if s.STAGE == "emerging":
                if s.TSUME >= status.phenology.params.TSUMEM:
                    status = self.next_stage(status)
            elif s.STAGE == 'vegetative':
                if s.DVS >= 1.0:
                    status = self.next_stage(status)
                    s.DVS = 1.0
            elif s.STAGE == 'reproductive':
                if s.DVS >= status.phenology.params.DVSEND:
                    status = self.next_stage(status)
            elif s.STAGE == 'mature':
                pass
            else:  # Problem no stage defined
                msg = "No STAGE defined in phenology submodule"
                raise Exception(msg)

        except  Exception as e:
            print('Error in method integrate of class Phenology:' + str(e))

        return status

    def runstep(self, status):
        """Calculates the rates for phenological development
        """
        try:
            r = status.rates
            s = status.states

            # if we are at sowing/emergence day
            if status.day == status.sowing_emergence_day:
                # Define initial stage type (emergence/sowing) and fill the
                # respective day of sowing/emergence (DOS/DOE)
                if status.phenology.params.CROP_START_TYPE == "emergence" :
                    s.STAGE = "vegetative"
                    s.DOE = status.day
                    s.DOS = None



                elif status.phenology.params.CROP_START_TYPE == "sowing":
                    s.STAGE = "emerging"
                    s.DOS = status.day
                    s.DOE = None

                else:
                    msg = "Unknown start type: %s" % status.phenology.params.CROP_START_TYPE
                    raise Exception(msg)

            if stopAtMaturity and s.DVS >= status.phenology.params.DVSEND:
                return status

            if s.DOE is None and s.DOS is None:  # before sowing and emergence
                return status

            # Day length sensitivity
            status.DVRED = 1.
            if status.phenology.params.IDSL >= 1:
                status.DVRED = limit(0., 1., (status.astrodata.DAYLP - status.phenology.params.DLC) / (
                            status.phenology.params.DLO - status.phenology.params.DLC))

            # Vernalisation NOTE: moved at the same level of the other components
            # ver=vernalisation()
            # status.VERNFAC = 1.
            # if status.phenology.params.IDSL >= 2:
            #     if s.STAGE == 'vegetative':
            #         status=ver.calc_rates(status)

            # Development rates
            if s.STAGE == "emerging":
                status.rates.DTSUME = limit(0., (status.phenology.params.TEFFMX - status.phenology.params.TBASEM),
                                            (status.states.TEMP - status.phenology.params.TBASEM))
                status.rates.DTSUM = 0.
                status.rates.DVR = 0.

            elif s.STAGE == 'vegetative':
                status.rates.DTSUME = 0.
                status.rates.DTSUM = status.phenology.params.DTSMTB(status.states.TEMP) * status.VERNFAC * status.DVRED
                status.rates.DVR = r.DTSUM / status.phenology.params.TSUM1

            elif s.STAGE in ['reproductive', 'mature']:
                status.rates.DTSUME = 0.
                status.rates.DTSUM = status.phenology.params.DTSMTB(status.states.TEMP)
                status.rates.DVR = r.DTSUM / status.phenology.params.TSUM2

            else:  # Problem: no stage defined
                msg = "Unrecognized STAGE defined in phenology submodule: %s"
                raise Exception(msg, status.states.STAGE)
        except  Exception as e:
            print('Error in method runstep of class Phenology:' + str(e))

        return status;
