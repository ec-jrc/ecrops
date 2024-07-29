# -*- coding: utf-8 -*-
#
# This component was derived from Hermes model (by professor Kurt Christian Kersebaum (Leibniz Centre for Agricultural Landscape Research)) and traslated and adapted by JRC for the eCrops framework
# European Commission, Joint Research Centre, March 2023


from ..Printable import Printable
import math
from ecrops.Step import Step

class HermesRootDepth(Step):
    """Calculation of root distribution and root length density. Used by HERMES for water uptake"""

    def getparameterslist(self):
        return {
            "IncreaseRootingDepth": {
                "Description": "Increase rooting depth function of cumulated degrees",
                "Type": "Number",
                "Mandatory": "True",
                "UnitOfMeasure": "mm/C"}

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
        status.hermesrootdepth = Printable()
        status.hermesrootdepth.params = Printable()
        status.hermesrootdepth.params.IncreaseRootingDepth = status.Hermes_IncreaseRootingDepth
        status.hermesrootdepth.hermes_roots_layer_data = []
        return status

    def initialize(self, status):
        status.hermesrootdepth.Veloc = status.hermesrootdepth.params.IncreaseRootingDepth / 200
        status.hermesrootdepth.TSumBase = math.log(0.35 ** (1 / 1.8) - 0.081476,
                                                   math.exp(-status.hermesrootdepth.Veloc))
        status.hermesrootdepth.cumuldegreeedays = 0
        status.hermesrootdepth.rootdepth = 0

        return status

    def runstep(self, status):
        states = status.states
        if (states.DOE is None or status.day < states.DOE) or (states.DOE is not None and status.day >= states.DOE and (
                states.DOM is not None and status.day >= states.DOM)):  # execute only after emergence and before maturity
            return status


        status.hermesrootdepth.QREZ = max((0.081476 + math.exp(-status.hermesrootdepth.Veloc * (
                status.hermesrootdepth.cumuldegreeedays + status.hermesrootdepth.TSumBase))) ** 1.8, 0.0409)

        if status.hermesrootdepth.QREZ > .35 :
            status.hermesrootdepth.QREZ = .35

        if status.hermesrootdepth.QREZ < 4.5/states.RDM :# limit to max root depth (states.RDM )
            status.hermesrootdepth.QREZ = 4.5 /states.RDM

        status.hermesrootdepth.rootdepth = 4.5 / status.hermesrootdepth.QREZ
        i = 0
        for d in status.hermesrootdepth.hermes_roots_layer_data:
            status.hermesrootdepth.hermes_roots_layer_data[i].cumulativePercentageOfRootUntilLayer = (1 - math.exp(
                -status.hermesrootdepth.QREZ * status.hermesrootdepth.hermes_roots_layer_data[i].lowerBoundary)) * 100

            #if the layer starts up the actual root depth, but end below, the 100% of the roots is above or in this layer.
            if status.hermesrootdepth.hermes_roots_layer_data[i].upperBoundary < status.hermesrootdepth.rootdepth and status.hermesrootdepth.hermes_roots_layer_data[i].lowerBoundary >= status.hermesrootdepth.rootdepth:
                status.hermesrootdepth.hermes_roots_layer_data[i].cumulativePercentageOfRootUntilLayer = 100

            #if the layer starts below the actual root depth, the 100% of the roots is above.
            if status.hermesrootdepth.hermes_roots_layer_data[i].upperBoundary >= status.hermesrootdepth.rootdepth:
                status.hermesrootdepth.hermes_roots_layer_data[i].cumulativePercentageOfRootUntilLayer = 100
            i = i + 1
        i = 0
        for d in status.hermesrootdepth.hermes_roots_layer_data:
            if i == 0:
                status.hermesrootdepth.hermes_roots_layer_data[i].percentageOfRootInLayer = \
                    status.hermesrootdepth.hermes_roots_layer_data[i].cumulativePercentageOfRootUntilLayer
            else:
                status.hermesrootdepth.hermes_roots_layer_data[i].percentageOfRootInLayer = \
                    status.hermesrootdepth.hermes_roots_layer_data[i].cumulativePercentageOfRootUntilLayer - status.hermesrootdepth.hermes_roots_layer_data[i-1].cumulativePercentageOfRootUntilLayer
            i = i + 1
        return status

    def integrate(self, status):
        return status
