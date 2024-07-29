import numpy as np

from ..Printable import Printable
from ecrops.Step import Step

class LinkSoilToNitrogen(Step):
    """ This step links soil properties to Nitrogen steps"""

    def getparameterslist(self):
        return {}#no parameters in this step

    def getinputslist(self):
        return {
            # to be implemented
        }

    def getoutputslist(self):
        return {
            #to be implemented
        }

    def setparameters(self,status):
        #initialize the data structures for nitrogen components
        status.hermesnitrogen = Printable()
        status.hermesnitrogen.params = Printable()
        status.hermestransport = Printable()
        status.hermestransport.params = Printable()
        status.hermesmineralization = Printable()
        status.hermesmineralization.params = Printable()
        status.hermesdenitrification = Printable()
        status.hermesdenitrification.params = Printable()
        status.hermesmaximumdiffusivetransport = Printable()
        status.hermesmaximumdiffusivetransport.params = Printable()
        status.hermesnitrogenstress = Printable()
        status.hermesnitrogenstress.params = Printable()
        status.hermesnuptake = Printable()
        status.hermesnuptake.params = Printable()

        # number of layers, taken from soil data
        status.hermesnitrogen.N = len(status.soildata['SOIL_LAYERS'])
        status.hermestransport.N = status.hermesnitrogen.N

        #initialize parameters

        # Faktor for diffusivity: depending on main soil texture (sand = 0.004, silt= 0.002, loam = 0.005, and clay 0.001)
        status.hermestransport.params.AD = status.soildata['AD']
        status.hermesnitrogen.params.AD = status.soildata['AD']
        status.hermesnitrogen.GRW = 200  # Groundwater level //TODO
        return status



    def initialize(self,status):

        #initialization of NAOS/NFOS values
        status.hermesmineralization.NAOS = np.ones((21),dtype=float)
        status.hermesmineralization.NFOS = np.ones((21), dtype=float)
        for i in range(0, status.hermesnitrogen.N):
            status.hermesmineralization.NAOS[i] = status.layeredwaterbalance.parameters.SOIL_LAYERS[i].NAOSInitial
            status.hermesmineralization.NFOS[i] = status.layeredwaterbalance.parameters.SOIL_LAYERS[i].NFOSInitial

        # initialization of PORGES values ( Total pore  space in layer Z(cm ^ 3 / cm ^ 3) )
        status.hermesmineralization.PORGES = 0.4 * np.ones((21),
                                                           dtype=float)
        for i in range(0, status.hermesnitrogen.N):
            status.hermesmineralization.PORGES[i] = status.layeredwaterbalance.parameters.SOIL_LAYERS[i].PORGES

        # initial values of C1
        status.hermestransport.C1 = 0 * np.ones((21), dtype=float)
        for i in range(0, status.hermesnitrogen.N):
            status.hermestransport.C1[i] = status.layeredwaterbalance.parameters.SOIL_LAYERS[i].C1Initial


        return status



    def runstep(self,status):
        # apply daily fertilization N, taken from nitrogenFertilization array
        # DSUMM = Summe of applied mineral N (kg N/ha)
        status.hermesmineralization.DSUMM += status.nitrogenFertilization[(status.day - status.first_day).days][0]

        return status


    def integrate(self,status):
        return status