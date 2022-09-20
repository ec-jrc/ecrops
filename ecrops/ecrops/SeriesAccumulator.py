class SeriesAccumulator:
    """
    SeriesAccumulator is a step used to collect some particular output variables into arrays which are organized by
    variable, and not by day. In this step we accumulate variables of Wofost (LAI, roots) and water balance (Soil
    moisture, transpiration, runoff,...)

    """

    def getparameterslist(self):
        return {}  # no parameters in this step

    def setparameters(self, status):
        return status

    def initialize(self, status):
        """ Initializes the variables to fill during the simulation"""
        status.dailyValuesOfSM = []
        status.dailyValuesOfLOSS = []
        status.dailyValuesOfRAIN = []
        status.dailyValuesOfEVAPOR = []
        status.dailyValuesOfTRAS = []
        status.dailyValuesOfRUNOFF = []
        status.dailyValuesOfROOT = []
        status.dailyValuesOfLAI = []
        status.dailyValuesOfTAGP = []
        return status

    def runstep(self, status):
        """ At every step fills the variables with values taken from status"""
        if hasattr(status, 'layeredwaterbalance') and hasattr(status.layeredwaterbalance.states, 'SM'):
            d = [status.doy]
            for il in range(0, status.layeredwaterbalance.parameters.NSL):
                d.append(status.layeredwaterbalance.parameters.SOIL_LAYERS[il].SM)
            status.dailyValuesOfSM.append(d)
            status.dailyValuesOfLOSS.append([status.doy, status.layeredwaterbalance.rates.LOSS])
            status.dailyValuesOfRAIN.append([status.doy, status.layeredwaterbalance.rates.RAIN])
            status.dailyValuesOfEVAPOR.append([status.doy, status.layeredwaterbalance.rates.EVS])
            status.dailyValuesOfTRAS.append([status.doy, status.layeredwaterbalance.rates.WTRA])
            status.dailyValuesOfRUNOFF.append([status.doy, status.layeredwaterbalance.rates.SR])
            status.dailyValuesOfROOT.append([status.doy, status.layeredwaterbalance.states.RD])
        if hasattr(status, 'classicwaterbalance') and hasattr(status.classicwaterbalance.states, 'SM'):
            d = [status.doy]
            d.append(status.classicwaterbalance.states.SM)
            d.append(status.classicwaterbalance.states.SMUR)
            status.dailyValuesOfSM.append(d)
            status.dailyValuesOfLOSS.append([status.doy, status.classicwaterbalance.rates.LOSS])
            status.dailyValuesOfRAIN.append([status.doy, status.classicwaterbalance.rates.RAIN])
            status.dailyValuesOfEVAPOR.append([status.doy, status.classicwaterbalance.rates.EVS])
            status.dailyValuesOfTRAS.append([status.doy, status.classicwaterbalance.rates.WTRA])
            status.dailyValuesOfRUNOFF.append([status.doy, 0])
            status.dailyValuesOfROOT.append([status.doy, status.classicwaterbalance.states.RD])
        if hasattr(status, 'states'):
            if hasattr(status.states, 'LAI'):
                status.dailyValuesOfLAI.append([status.doy, status.states.LAI])
            if hasattr(status.states, 'TAGP'):
                status.dailyValuesOfTAGP.append([status.doy, status.states.TAGP])

        return status



    def integrate(self, status):
        """Does nothing"""
        return status
