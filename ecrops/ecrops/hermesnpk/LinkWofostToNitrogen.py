from ..Printable import Printable
from ecrops.Step import Step
class LinkWofostToNitrogen(Step):
    """This step passes Wofost data (biomasses, phenology data, root depth) to nitrogen steps"""

    def getparameterslist(self):
        return {}  # no parameters in this step

    def getinputslist(self):
        return {
            # to be implemented
        }

    def getoutputslist(self):
        return {
            #to be implemented
        }

    def setparameters(self, status):
        status.hermesnpk = Printable()
        status.hermesnpk.parameters = Printable()
        status.hermesnpk.parameters.WGMAX_before_emerging=status.allparameters['WGMAX_before_emerging']
        status.hermesnpk.parameters.WGMAX_emerging = status.allparameters['WGMAX_emerging']
        status.hermesnpk.parameters.WGMAX_vegetative = status.allparameters['WGMAX_vegetative']
        status.hermesnpk.parameters.WGMAX_reproductive = status.allparameters['WGMAX_reproductive']
        status.hermesnpk.parameters.WGMAX_mature = status.allparameters['WGMAX_mature']
        status.hermesnpk.parameters.NITROGEN_FRUCHT = status.allparameters['NITROGEN_FRUCHT']
        return status

    def initialize(self, status):

        status.hermesnitrogen.WUGEH = 0.017  # N-content roots concentration (kg N / kg biomass)
        status.hermesnitrogen.GEHOB = 0.06  # N-content above ground biomass concentration (kg N / kg biomass)

        return self.runstep(status)

    def runstep(self, status):

        if status.states.DOS is None and status.states.DOE is None:
            status.hermestransport.SAAT = 0
        else:
            if status.states.DOS is not None:
                status.hermestransport.SAAT = status.states.DOS.timetuple().tm_yday  # sowing doy
            else:
                status.hermestransport.SAAT = status.states.DOE.timetuple().tm_yday  # emergence doy

        status.hermesnitrogen.FRUCHT = status.hermesnpk.parameters.NITROGEN_FRUCHT  # crop acronym
        status.hermesnuptake.FRUCHT = status.hermesnpk.parameters.NITROGEN_FRUCHT  # crop acronym
        status.hermesnitrogen.OBMAS = status.states.TAGP  # aboveground biomass
        status.hermesnitrogen.OBALT = status.states.TAGP_previousday  # TODO  #aboveground biomass of previous day
        status.hermesnitrogen.WUMAS = status.states.WRT  # roots biomass
        status.hermesnitrogen.WUMALT = status.states.WRT_previousDay  # roots biomass of previous day
        status.hermesnitrogen.WUORG = status.states.TWSO  # dry mass of organs
        status.hermesnitrogen.DGORG = status.states.DWSO  # dead organs biomass
        status.hermesnitrogen.PHYLLO = status.states.TSUM  # cumulative development effective temperature sum (°C days)
        status.hermesnuptake.PHYLLO = status.states.TSUM  # cumulative development effective temperature sum (°C days)
        status.hermesnitrogen.TSUMEM = status.phenology.params.TSUMEM  # TSUMEM (SUM[0] in original hermes code)#TODO: check it is correct
        status.hermesnitrogen.tendsum = status.phenology.params.TSUM1 + status.phenology.params.TSUM2 + status.phenology.params.TSUMEM  # Total temperature sum of all stages
        import math
        max_crop_root_depth_dm = int(math.floor(status.allparameters['RDMCR'] / 10))  # conversion cm-dm
        status.hermesnitrogen.WURZMAX = max_crop_root_depth_dm  # 11  # in dm # soil specific effective rooting depth. We set it to the max crop depth
        status.hermesnitrogen.WUMAXPF = max_crop_root_depth_dm  # 11  # in dm # crop specific effective rooting depth. We set it to the max crop depth
        status.hermestransport.OUTN = max_crop_root_depth_dm  # Depth for seepage and N-leaching (to be defined by user) (dm). We set it to the max crop depth

        # N-content root end of phase. It is a parameter dependent on the stage
        try:
            if status.states.STAGE == "emerging":
                status.hermesnitrogen.WGMAX = status.hermesnpk.parameters.WGMAX_emerging

            elif status.states.STAGE == "vegetative":
                status.hermesnitrogen.WGMAX = status.hermesnpk.parameters.WGMAX_vegetative

            elif status.states.STAGE == "reproductive":
                status.hermesnitrogen.WGMAX = status.hermesnpk.parameters.WGMAX_reproductive

            elif status.states.STAGE == "mature":
                status.hermesnitrogen.WGMAX = status.hermesnpk.parameters.WGMAX_mature
            else:  # before emerging
                status.hermesnitrogen.WGMAX = status.hermesnpk.parameters.WGMAX_before_emerging  # before emerging
        except:
            status.hermesnitrogen.WGMAX = status.hermesnpk.parameters.WGMAX_before_emerging  # before emerging

        return status

    def integrate(self, status):
        return status
