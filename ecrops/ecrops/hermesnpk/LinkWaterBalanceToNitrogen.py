import numpy as np

from ..Printable import Printable
from ecrops.Step import Step

class LinkWaterBalanceToNitrogen(Step):
    """This step links water balance output to nitrogen steps"""

    def getparameterslist(self):
        return {}#no parameters in this step

    def setparameters(self,status):

        return status

    def getinputslist(self):
        return {
            # to be implemented
        }

    def getoutputslist(self):
        return {
            #to be implemented
        }


    def initialize(self,status):

        #TODO verify which is the difference between WNOR e W. For now we set them equals to fc

        status.hermesmineralization.WG =np.zeros(( 21), dtype=float) #actual sm
        status.hermesmineralization.WNOR = np.zeros((21), dtype=float)  # fc
        status.hermesmineralization.WMIN = np.zeros((21), dtype=float)  # wp
        status.hermesmineralization.W = np.zeros((21), dtype=float)  # fc

        status.hermestransport.WG = np.zeros(( 21), dtype=float)#actual sm
        status.hermestransport.W = np.zeros((21), dtype=float)  # fc
        status.hermestransport.WNOR = np.zeros((21), dtype=float)  # fc
        status.hermestransport.WMIN = np.zeros((21), dtype=float)  # wp

        status.hermesnitrogen.WG = np.zeros(( 21), dtype=float)#actual sm
        status.hermesnitrogen.W = np.zeros((21), dtype=float)  # fc
        status.hermesnitrogen.WNOR = np.zeros((21), dtype=float)  # fc
        status.hermesnitrogen.WMIN = np.zeros((21), dtype=float)  # wp


        status.hermesnitrogen.TP= np.zeros(( 21), dtype=float)#water uptake
        status.hermestransport.Q1 = np.zeros(( 21), dtype=float)# Water flux through lower boundary of layer z (cm/d) (coming from water submodel)
        return self.runstep(status)



    def runstep(self,status):

        for i in range(0,status.hermesnitrogen.N):
            status.hermesmineralization.WG[i] = status.layeredwaterbalance.parameters.SOIL_LAYERS[i].SM #actual sm
            status.hermesmineralization.WMIN[i] = status.layeredwaterbalance.parameters.SOIL_LAYERS[i].SMW  # wp
            status.hermesmineralization.WNOR[i] = status.layeredwaterbalance.parameters.SOIL_LAYERS[i].SM0  # fc
            status.hermesmineralization.W[i] = status.layeredwaterbalance.parameters.SOIL_LAYERS[i].SM0 # fc

            status.hermestransport.W[i] = status.layeredwaterbalance.parameters.SOIL_LAYERS[i].SM0 # fc
            status.hermestransport.WMIN[i] = status.layeredwaterbalance.parameters.SOIL_LAYERS[i].SMW  # wp
            status.hermestransport.WNOR[i] = status.layeredwaterbalance.parameters.SOIL_LAYERS[i].SM0  # fc
            status.hermestransport.WG[i] = status.layeredwaterbalance.parameters.SOIL_LAYERS[i].SM #actual sm


            status.hermesnitrogen.WG[i] = status.layeredwaterbalance.parameters.SOIL_LAYERS[i].SM #actual sm
            status.hermesnitrogen.WMIN[i] = status.layeredwaterbalance.parameters.SOIL_LAYERS[i].SMW  # wp
            status.hermesnitrogen.WNOR[i] = status.layeredwaterbalance.parameters.SOIL_LAYERS[i].SM0  # fc
            status.hermesnitrogen.W[i] = status.layeredwaterbalance.parameters.SOIL_LAYERS[i].SM0  # fc

            if status.rates.TRALY!=0:
                status.hermesnitrogen.TP[i] = status.rates.TRALY[i] #transpiration actual or potential??todo??
            else:
                status.hermesnitrogen.TP[i] =0
            status.hermestransport.Q1[i] = status.layeredwaterbalance.parameters.SOIL_LAYERS[i].DownwardFLOWAtBottomOfLayer# Water flux through lower boundary of layer z (cm/d) (coming from water submodel) #TODO:check is correct varianle
            status.hermesnitrogen.MAXSOILDEPTH = status.layeredwaterbalance.parameters.SOIL_LAYERS[i].LBSL/10 #conversion cm->dm #depth of the last layer
            status.hermesmineralization.WRED= (status.layeredwaterbalance.parameters.SOIL_LAYERS[i].WCW + \
                                                    0.66*(status.layeredwaterbalance.parameters.SOIL_LAYERS[i].WCFC-status.layeredwaterbalance.parameters.SOIL_LAYERS[i].WCW))/100. #wred is calculated using the last layer FC and WP, correct?
        return status


    def integrate(self,status):
        return status