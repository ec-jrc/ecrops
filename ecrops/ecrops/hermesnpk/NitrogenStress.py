# -*- coding: utf-8 -*-
#
# This component was derived from Hermes model (by professor Kurt Christian Kersebaum (Leibniz Centre for Agricultural Landscape Research)) and traslated and adapted by JRC for the eCrops framework
# European Commission, Joint Research Centre, March 2023



import numpy as np

from ..Printable import Printable
import math
from ecrops.Step import Step

class NitrogenStress(Step):
    """Nitrogen stress on plant growth from Hermes. Copied from file crop.go rows 507-525"""

    def getparameterslist(self):
        return {
        }

    def getinputslist(self):
        return {
            # to be implemented
        }

    def getoutputslist(self):
        return {
            #to be implemented
        }

    def setparameters(self, status):

        return status

    def initialize(self, status):

        status.hermesnitrogenstress.subd = 1  # number of subdivisions in a day
        status.hermesnitrogenstress.wdt = 1  # fraction of day ( the time step of one day is sometimes reduced when water flux becommes too high)

        # initialize outputs
        status.hermesnitrogenstress.REDUK = 0  # stress factor nitrogen deficiency (0-1)
        status.hermesnitrogenstress.REDUKSUM = 0  # cumulative stress factor nitrogen deficiency (0-1)

        return status

    def runstep(self, status):

        if hasattr(status.hermesnitrogen, 'FRUCHT') and status.hermesnitrogen.FRUCHT == "WW ":
            status.hermesnitrogenstress.NGEFKT = 1  # crop N-content function no. (critical and max. N-contents). value 1 is for winter wheat
        else:  # TODO: manage other crops
            status.hermesnitrogenstress.NGEFKT = 2  # crop N-content function no. (critical and max. N-contents). # value 2 is for maize

        # estimation of stress factors (N and water)
        GEHALT = status.hermesnitrogen.GEHOB
        if status.states.DVS > 0:  # todo: check the condition on DVS is correct
            if status.hermesnitrogen.GEHOB < status.hermesnuptake.GEHMIN:
                MININ = 0
                if status.hermesnitrogenstress.NGEFKT == 1:
                    MININ = 0.005
                else:
                    MININ = 0.004

                if status.hermesnitrogen.GEHOB <= MININ:
                    status.hermesnitrogenstress.REDUK = 0.0
                else:
                    AUX = (status.hermesnitrogen.GEHOB - MININ) / (status.hermesnuptake.GEHMIN - MININ)
                    status.hermesnitrogenstress.REDUK = math.pow((1 - math.exp(1 + 1 / (AUX - 1))), 2)

            else:
                status.hermesnitrogenstress.REDUK = 1.

            status.hermesnitrogenstress.REDUKSUM = status.hermesnitrogenstress.REDUKSUM + status.hermesnitrogenstress.REDUK

        return status

    def integrate(self, status):
        return status
