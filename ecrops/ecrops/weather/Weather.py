from collections import deque
from math import exp, isnan
from ecrops.wofost_util.util import reference_ET, doy
from ..wofost import astro


class Weather:
    """This step reads weather data from input 'status.weather.WeatherDataArray' for the current day
    and fills the status weather variables (for example status.weather.TEMP_MAX, status.weather.IRRAD, status.weather.RAIN).

    Expected weather variables in 'status.weather.WeatherDataArray' and their unit of measure:
    TEMP_MAX Celsius
    TEMP_Min Celsius
    IRRAD J/m^2 *day
    RAIN cm
    WIND m/s
    RH perc
    E0,ES0,ET0 cm
    """

    def getparameterslist(self):
        """no parameters in this step"""
        return {}

    def setparameters(self, status):
        """no parameters in this step"""

        #if WeatherColumnForVariable was not defined in the model configuration, we use this default setting
        if not hasattr(status.weather,'WeatherColumnForVariable'):
            status.weather.WeatherColumnForVariable= {'TEMP_MAX': 0, 'TEMP_MIN': 1, 'IRRAD': 2, 'RAIN': 3, 'WIND': 4, 'RH': 5, 'E0': 6, 'ES0': 7, 'ET0': 8, 'TEMP_AVG': 9}

        return status

    def runstep(self, status):

        status=self.setweatherdata(status)

        # dfumagalli -28-07-2021 : modification to make it equal to bioma implementation
        # added IF to start calculation of minumum temperature 7 days average only after emergence
        if not hasattr(status,"START_EVENT"):
            if(status.states.DOE is not None and status.states.DOE <= status.day):
                status.weather.TMINRA = (self._7day_running_avg(status))
        else:
            if (status.START_EVENT!=1 and status.simulation_start_day <= status.day) or (status.START_EVENT==1 and status.states.DOE is not None and status.states.DOE <= status.day):
                status.weather.TMINRA = (self._7day_running_avg(status))
            else:
                status.weather.TMINRA = None

        return status

    def initialize(self, status):
        """ initialize the weather variables"""

        # initialize TMNSAV (7-days running mean of minimum temperature) to a deque of size 7
        status.weather.TMNSAV = deque(maxlen=7)
        status.weather.TMINRA = None
        return self.setweatherdata(status)

    def setweatherdata(self,status):

        """ Every day moves data from tatus.weather.WeatherDataArray to the proper status weather variables"""
        status.doy = doy(status.day)
        number_progr_days = (status.day - status.first_day).days

        # extract data from input data array
        status.weather.TEMP_MAX = (status.weather.WeatherDataArray[number_progr_days][
                                       status.weather.WeatherColumnForVariable['TEMP_MAX']])  # C
        status.weather.TEMP_MIN = (status.weather.WeatherDataArray[number_progr_days][
                                       status.weather.WeatherColumnForVariable['TEMP_MIN']])  # C

        # if daily avg temperature is in the input use it, otherwise calculate it as (tmax+tmin)/2
        if 'TEMP_AVG' in status.weather.WeatherColumnForVariable:
            status.weather.TEMP = (status.weather.WeatherDataArray[number_progr_days][
                                       status.weather.WeatherColumnForVariable['TEMP_AVG']])  # C
        else:
            status.weather.TEMP = ((status.weather.TEMP_MAX + status.weather.TEMP_MIN) / 2)

        status.weather.DTEMP = ((status.weather.TEMP_MAX + status.weather.TEMP) / 2)

        status.weather.IRRAD = (status.weather.WeatherDataArray[number_progr_days][
                                    status.weather.WeatherColumnForVariable['IRRAD']])  # J/m^2 *day


        status.weather.RAIN = (
        status.weather.WeatherDataArray[number_progr_days][status.weather.WeatherColumnForVariable['RAIN']])  # cm

        # if wind is not present in the weather dataset, it is set to zero
        if 'WIND' in status.weather.WeatherColumnForVariable:
            status.weather.WIND = (status.weather.WeatherDataArray[number_progr_days][
                                       status.weather.WeatherColumnForVariable['WIND']])  # m/s
        else:
            status.weather.WIND = 0

        # if relative humidity is not present in the weather dataset, it is set to 80%
        if 'RH' in status.weather.WeatherColumnForVariable:
            status.weather.RH = (
            status.weather.WeatherDataArray[number_progr_days][status.weather.WeatherColumnForVariable['RH']])
        else:
            status.weather.RH = 80

        # calculate here saturated VAP from temperatures and RH
        SVAP = 6.10588 * exp(17.32491 * status.weather.TEMP / (status.weather.TEMP + 238.102))
        status.weather.VAP = (SVAP * status.weather.RH / 100)

        # calculate astronomical data
        a = astro.Astro()
        status = a.calc_astro(status)

        # retrieve the evapotraspiration values from input array, or calculate them if not present
        if 'E0' in status.weather.WeatherColumnForVariable and 'ES0' in status.weather.WeatherColumnForVariable and 'ET0' in status.weather.WeatherColumnForVariable:
            status.weather.E0 = (
                status.weather.WeatherDataArray[number_progr_days][
                    status.weather.WeatherColumnForVariable['E0']])  # cm
            status.weather.ES0 = (
                status.weather.WeatherDataArray[number_progr_days][
                    status.weather.WeatherColumnForVariable['ES0']])  # cm
            status.weather.ET0 = (
                status.weather.WeatherDataArray[number_progr_days][
                    status.weather.WeatherColumnForVariable['ET0']])  # cm

        else:
            angstA = 0.25
            angstB = 0.5
            status.weather.E0, status.weather.ES0, status.weather.ET0 = reference_ET(DAY=status.day, LAT=status.LAT,
                                                                                     ELEV=0,
                                                                                     TMIN=status.weather.TEMP_MIN,
                                                                                     TMAX=status.weather.TEMP_MAX,
                                                                                     IRRAD=status.weather.IRRAD,
                                                                                     VAP=status.weather.VAP,
                                                                                     WIND=status.weather.WIND,
                                                                                     ANGSTA=angstA, ANGSTB=angstB,
                                                                                     ATMTR=status.astrodata.ATMTR,
                                                                                     ANGOT=status.astrodata.ANGOT)

        return status

    def _7day_running_avg(self, status):
        """Calculate 7-days running mean of minimum temperature.
        """
        # Append new value at the left side of the deque
        status.weather.TMNSAV.appendleft(status.weather.TEMP_MIN)
        # Return the new calculated average
        return sum(status.weather.TMNSAV) / len(status.weather.TMNSAV)

    def integrate(self, status):
        """Does nothing"""
        return status
