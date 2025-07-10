# -*- coding: utf-8 -*-
# This component is derived from PCSE software/Wofost model
# (Copyright @ 2004-2014 Alterra, Wageningen-UR; Allard de Wit allard.dewit@wur.nl, April 2014)
# and modified by EC-JRC for the eCrops framework under the European Union Public License (EUPL), Version 1.2
# European Commission, Joint Research Centre, March 2023


from ..wofost_util.Afgen import Afgen
from ..Printable import Printable
from ..wofost_util.util import limit
from ecrops.Step import Step

class Vernalisation(Step):
    """ Modification of phenological development due to vernalisation.

    The vernalization approach here is based on the work of Lenny van Bussel
    (2011), which in turn is based on Wang and Engel (1998). The basic
    principle is that winter wheat needs a certain number of days with temperatures
    within an optimum temperature range to complete its vernalisation
    requirement. Until the vernalisation requirement is fulfilled, the crop
    development is delayed.

    The rate of vernalization (VERNR) is defined by the temperature response
    function VERNRTB. Within the optimal temperature range 1 day is added
    to the vernalisation state (VERN). The reduction on the phenological
    development is calculated from the base and saturated vernalisation
    requirements (VERNBASE and VERNSAT). The reduction factor (VERNFAC) is
    scaled linearly between VERNBASE and VERNSAT.

    A critical development stage (VERNDVS) is used to stop the effect of
    vernalisation when this DVS is reached. This is done to improve model
    stability in order to avoid that Anthesis is never reached due to a
    somewhat too high VERNSAT. Nevertheless, a warning is written to the log
    file, if this happens.

    * Van Bussel, 2011. From field to globe: Upscaling of crop growth modelling.
      Wageningen PhD thesis. http://edepot.wur.nl/180295
    * Wang and Engel, 1998. Simulation of phenological development of wheat
      crops. Agric. Systems 58:1 pp 1-24

    *Simulation parameters* (provide in cropdata dictionary)

    ======== ============================================= =======  ============
     Name     Description                                   Type     Unit
    ======== ============================================= =======  ============
    VERNSAT  Saturated vernalisation requirements           SCr        days
    VERNBASE Base vernalisation requirements                SCr        days
    VERNRTB  Rate of vernalisation as a function of daily   TCr        -
             mean temperature.
    VERNDVS  Critical development stage after which the     SCr        -
             effect of vernalisation is halted
    ======== ============================================= =======  ============

    **State variables**

    ============ ================================================= ==== ========
     Name        Description                                       Pbl   Unit
    ============ ================================================= ==== ========
    VERN         Vernalisation state                                N    days
    DOV          Day when vernalisation requirements are            N    -
                 fulfilled.
    ISVERNALISED Flag indicated that vernalisation                  Y    -
                 requirement has been reached
    ============ ================================================= ==== ========


    **Rate variables**

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    VERNR    Rate of vernalisation                              N     -
    VERNFAC  Reduction factor on development rate due to        Y     -
             vernalisation effect.
    =======  ================================================= ==== ============


    **External dependencies:**

    ============ =============================== ========================== =====
     Name        Description                         Provided by             Unit
    ============ =============================== ========================== =====
    DVS          Development Stage                 Phenology                 -
                 Used only to determine if the
                 critical development stage for
                 vernalisation (VERNDVS) is
                 reached.
    ============ =============================== ========================== =====
    """

    def getparameterslist(self):
        return {
            "IDSL": {
                "Description": "Switch for phenological development options: temperature only (IDSL=0), daylength (IDSL=1) and including vernalization (IDSL>=2)",
                "Type": "Number", "Mandatory": "True", "UnitOfMeasure": "unitless"},
            "VERNSAT": {"Description": "Saturated vernalisation requirements", "Type": "Number", "Mandatory": "True",
                        "UnitOfMeasure": "days"},
            "VERNBASE": {"Description": "Base vernalisation requirements", "Type": "Number", "Mandatory": "True",
                         "UnitOfMeasure": "days"},
            "VERNRTB": {"Description": "Rate of vernalisation as a function of daily mean temperature", "Type": "Array",
                        "Mandatory": "True",
                        "UnitOfMeasure": "unitless"},
            "VERNDVS": {"Description": "Critical development stage after which the effect of vernalisation is halted",
                        "Type": "Number", "Mandatory": "True",
                        "UnitOfMeasure": "unitless"}
        }

    def setparameters(self, status):
        try:
            status.vernalisation = Printable()
            status.vernalisation.params = Printable()
            cropparams = status.allparameters
            if 'IDSL' in cropparams:
                status.vernalisation.params.IDSL = cropparams['IDSL']
            else:
                status.vernalisation.params.IDSL = 0  # if no IDSL param provided, set it to 0 (default)
            if 'VERNSAT' in cropparams:
                status.vernalisation.params.VERNSAT = cropparams['VERNSAT']
            if 'VERNBASE' in cropparams:
                status.vernalisation.params.VERNBASE = cropparams['VERNBASE']
            if 'VERNRTB' in cropparams and cropparams['VERNRTB'] is not None:
                status.vernalisation.params.VERNRTB = Afgen(cropparams['VERNRTB'])
            if 'VERNDVS' in cropparams:
                status.vernalisation.params.VERNDVS = cropparams['VERNDVS']
        except Exception as e:
            print('Error in method setparameters of class vernalisation:' + str(e))
            pass  # Some crops do not require vernalization parameters, so let this pass
        return status

    def initialize(self, status):
        try:
            if status.vernalisation.params.IDSL >= 2:  # if IDSL <2 vernalization does nothing
                status.vernalisation.VERN = 0.
                status.VERNFAC = 0.
                status.vernalisation.DOV = None
                status.vernalisation.ISVERNALISED = False
                status.vernalisation.VERNR = 0.
                status.vernalisation._force_vernalisation = False
        except  Exception as e:
            print('Error in method initialize of class vernalisation:' + str(e))
        return status

    def runstep(self, status):
        try:

            if status.states.DOE is None and status.states.DOS is None:  # before sowing and emergence
                return status

            if status.vernalisation.params.IDSL >= 2:  # if IDSL <2 vernalization does nothing
                s = status.states
                if s.STAGE == 'vegetative':
                    if not status.vernalisation.ISVERNALISED:
                        if s.DVS < status.vernalisation.params.VERNDVS:
                            status.vernalisation.VERNR = status.vernalisation.params.VERNRTB(status.states.TEMP)
                            r = (status.vernalisation.VERN - status.vernalisation.params.VERNBASE) / (
                                        status.vernalisation.params.VERNSAT - status.vernalisation.params.VERNBASE)
                            status.VERNFAC = limit(0., 1., r)
                        else:
                            status.vernalisation.VERNR = 0.
                            status.VERNFAC = 1.0
                            status.vernalisation._force_vernalisation = True
                    else:
                        status.vernalisation.VERNR = 0.
                        status.VERNFAC = 1.0
        except Exception as e:
            print('Error in method runstep of class vernalisation:' + str(e))
        return status

    def integrate(self, status):
        try:
            if status.states.DOE is None and status.states.DOS is None:  # before sowing and emergence
                return status

            if status.vernalisation.params.IDSL >= 2:  # if IDSL <2 vernalization does nothing
                s = status.states
                if s.STAGE == 'vegetative':
                    status.vernalisation.VERN += status.vernalisation.VERNR

                    if status.vernalisation.VERN >= status.vernalisation.params.VERNSAT:  # Vernalisation requirements reached
                        status.vernalisation.ISVERNALISED = True
                        if status.vernalisation.DOV is None:
                            status.vernalisation.DOV = status.day


                    elif status.vernalisation._force_vernalisation:  # Critical DVS for vernalisation reached
                        # Force vernalisation, but do not set DOV
                        status.vernalisation.ISVERNALISED = True

                    else:  # Reduction factor for phenologic development
                        status.vernalisation.ISVERNALISED = False
        except Exception as e:
            print('Error in method integrate of class vernalisation:' + str(e))

        return status

    def getinputslist(self):
        return {

            "day": {"Description": "Current day", "Type": "Number", "UnitOfMeasure": "doy",
                    "StatusVariable": "status.day"},
            "DOS": {"Description": "Doy of sowing", "Type": "Number", "UnitOfMeasure": "doy",
                    "StatusVariable": "status.states.DOS"},
            "DOE": {"Description": "Doy of emergence", "Type": "Number", "UnitOfMeasure": "doy",
                    "StatusVariable": "status.states.DOE"},
            "STAGE": {"Description": "Phenological stage", "Type": "String", "UnitOfMeasure": "-",
                      "StatusVariable": "status.states.STAGE"},
            "DVS": {"Description": "Development stage", "Type": "Number", "UnitOfMeasure": "unitless",
                    "StatusVariable": "status.states.DVS"},
            "TEMP": {"Description": "Average daily temperature",
                     "Type": "Number", "UnitOfMeasure": "C",
                     "StatusVariable": "status.states.TEMP"},
            "VERN": {"Description": "Vernalisation state", "Type": "Boolean",
                     "UnitOfMeasure": "days",
                     "StatusVariable": "status.vernalisation.VERN"},
        }

    def getoutputslist(self):
        return {

            "DOV": {"Description": "Doy of vernalisation end", "Type": "Number", "UnitOfMeasure": "doy",
                    "StatusVariable": "status.vernalisation.DOV"},
            "ISVERNALISED": {"Description": "True if the crop is vernalised, False otherwise", "Type": "Boolean", "UnitOfMeasure": "doy",
                    "StatusVariable": "status.vernalisation.ISVERNALISED"},
            "VERN": {"Description": "Vernalisation state", "Type": "Number",
                             "UnitOfMeasure": "days",
                             "StatusVariable": "status.vernalisation.VERN"},
            "VERNR": {"Description": "Rate of vernalisation", "Type": "Number",
                     "UnitOfMeasure": "",
                     "StatusVariable": "status.vernalisation.VERNR"},
            "VERNFAC": {"Description": "Reduction factor on development rate due to vernalisation effect.", "Type": "Number",
                      "UnitOfMeasure": "",
                      "StatusVariable": "status.VERNFAC"},

        }
