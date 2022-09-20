"""Utilities for WOFOST simulation"""
from math import log10, cos, sin, asin, sqrt, exp
import datetime


Celsius2Kelvin = lambda x: x + 273.16
"""unit of measure conversion: C to Kelvin"""

hPa2kPa = lambda x: x / 10.
"""unit of measure conversion: hPa to kPa"""


SatVapourPressure = lambda temp: 0.6108 * exp((17.27 * temp) / (237.3 + temp))
""" Saturated Vapour pressure [kPa] at temperature temp [C] """


def isC3crop(crop):
    """Returns true if the crop is C3 """
    if crop == 2:
        return False
    else:
        return True


def limit(min, max, v):
    """limits the range of v between min and max """

    if min > max:
        raise RuntimeError("Min value (%f) larger than max (%f)" % (min, max))

    if v < min:  # V below range: return min
        return min
    elif v < max:  # v within range: return v
        return v
    else:  # v above range: return max
        return max


def wind10to2(wind10):
    """Converts windspeed at 10m to windspeed at 2m using log. wind profile
    """
    wind2 = wind10 * (log10(2. / 0.033) / log10(10 / 0.033))
    return wind2


def reference_ET(DAY, LAT, ELEV, TMIN, TMAX, IRRAD, VAP, WIND,
                 ANGSTA, ANGSTB, ATMTR, ANGOT, ETMODEL="PM", **kwargs):
    """Calculates reference evapotranspiration values E0, ES0 and ET0.

    The open water (E0) and bare soil evapotranspiration (ES0) are calculated with
    the modified Penman approach, while the references canopy evapotranspiration is
    calculated with the modified Penman or the Penman-Monteith approach, the latter
    is the default.

    Input variables::

        DAY     -  Python datetime.date object                      -
        LAT     -  Latitude of the site                          degrees
        ELEV    -  Elevation above sea level                        m
        TMIN    -  Minimum temperature                              C
        TMAX    -  Maximum temperature                              C
        IRRAD   -  Daily shortwave radiation                     J m-2 d-1
        VAP     -  24 hour average vapour pressure                 hPa
        WIND    -  24 hour average windspeed at 2 meter            m/s
        ANGSTA  -  Empirical constant in Angstrom formula           -
        ANGSTB  -  Empirical constant in Angstrom formula           -
        ETMODEL -  Indicates if the canopy reference ET should     PM|P
                   be calculated with the Penman-Monteith method
                   (PM) or the modified Penman method (P)

    Output is a tuple (E0, ES0, ET0)::

        E0      -  Penman potential evaporation from a free
                   water surface [mm/d]
        ES0     -  Penman potential evaporation from a moist
                   bare soil surface [mm/d]
        ET0     -  Penman or Penman-Monteith potential evapotranspiration from a
                   crop canopy [mm/d]

.. note:: The Penman-Monteith algorithm is valid only for a reference canopy and
    therefore it is not used to calculate the reference values for bare soil and
    open water (ES0, E0).

    The background is that the Penman-Monteith model is basically a surface
    energy balance where the net solar radiation is partitioned over latent and
    sensible heat fluxes (ignoring the soil heat flux). To estimate this
    partitioning, the PM method makes a connection between the surface
    temperature and the air temperature. However, the assumptions
    underlying the PM model are valid only when the surface where this
    partitioning takes place is the same for the latent and sensible heat
    fluxes.

    For a crop canopy this assumption is valid because the leaves of the
    canopy form the surface where both latent heat flux (through stomata)
    and sensible heat flux (through leaf temperature) are partitioned.
    For a soil, this principle does not work because when the soil is
    drying the evaporation front will quickly disappear below the surface
    and therefore the assumption that the partitioning surface is the
    same does not hold anymore.

    For water surfaces, the assumptions underlying PM do not hold
    because there is no direct relationship between the temperature
    of the water surface and the net incoming radiation as radiation is
    absorbed by the water column and the temperature of the water surface
    is co-determined by other factors (mixing, etc.). Only for a very
    shallow layer of water (1 cm) the PM methodology could be applied.

    For bare soil and open water the Penman model is preferred. Although it
    partially suffers from the same problems, it is calibrated somewhat
    better for open water and bare soil based on its empirical wind
    function.

    Finally, in crop simulation models the open water evaporation and
    bare soil evaporation only play a minor role (pre-sowing conditions
    and flooded rice at early stages), it is not worth investing much
    effort in improved estimates of reference value for E0 and ES0.
    """
    if ETMODEL not in ["PM", "P"]:
        msg = "Variable ETMODEL can have values 'PM'|'P' only."
        raise RuntimeError(msg)

    E0, ES0, ET0 = penman(DAY, LAT, ELEV, TMIN, TMAX, IRRAD, VAP, WIND,
                          ANGSTA, ANGSTB, ATMTR)
    if ETMODEL == "PM":
        ET0 = penman_monteith(DAY, LAT, ELEV, TMIN, TMAX, IRRAD, VAP, WIND, ANGOT)

    return float(E0 / 10.), float(ES0 / 10.), float(ET0 / 10.)


def penman(DAY, LAT, ELEV, TMIN, TMAX, AVRAD, VAP, WIND2, ANGSTA, ANGSTB, ATMTR):
    """Calculates E0, ES0, ET0 based on the Penman model.

     This routine calculates the potential evapo(transpi)ration rates from
     a free water surface (E0), a bare soil surface (ES0), and a crop canopy
     (ET0) in mm/d. For these calculations the analysis by Penman is followed
     (Frere and Popov, 1979;Penman, 1948, 1956, and 1963).
     Subroutines and functions called: ASTRO, LIMIT.

    Input variables::

        DAY     -  Python datetime.date object                                    -
        LAT     -  Latitude of the site                        degrees
        ELEV    -  Elevation above sea level                      m
        TMIN    -  Minimum temperature                            C
        TMAX    -  Maximum temperature                            C
        AVRAD   -  Daily shortwave radiation                   J m-2 d-1
        VAP     -  24 hour average vapour pressure               hPa
        WIND2   -  24 hour average windspeed at 2 meter          m/s
        ANGSTA  -  Empirical constant in Angstrom formula         -
        ANGSTB  -  Empirical constant in Angstrom formula         -

    Output is a tuple (E0,ES0,ET0)::

        E0      -  Penman potential evaporation from a free water surface [mm/d]
        ES0     -  Penman potential evaporation from a moist bare soil surface [mm/d]
        ET0     -  Penman potential transpiration from a crop canopy [mm/d]
    """
    # psychrometric instrument constant (mbar/Celsius-1)
    # albedo for water surface, soil surface and canopy
    # latent heat of evaporation of water (J/kg=J/mm)
    # Stefan Boltzmann constant (in J/m2/d/K4, e.g multiplied by 24*60*60)
    PSYCON = 0.67;
    REFCFW = 0.05;
    REFCFS = 0.15;
    REFCFC = 0.25
    LHVAP = 2.45E6;
    STBC = 5.670373E-8 * 24 * 60 * 60  # (=4.9E-3)

    # preparatory calculations
    # mean daily temperature and temperature difference (Celsius)
    # coefficient Bu in wind function, dependent on temperature
    # difference
    TMPA = (TMIN + TMAX) / 2.
    TDIF = TMAX - TMIN
    BU = 0.54 + 0.35 * limit(0., 1., (TDIF - 12.) / 4.)

    # barometric pressure (mbar)
    # psychrometric constant (mbar/Celsius)
    PBAR = 1013. * exp(-0.034 * ELEV / (TMPA + 273.))
    GAMMA = PSYCON * PBAR / 1013.

    # saturated vapour pressure according to equation of Goudriaan
    # (1977) derivative of SVAP with respect to temperature, i.e.
    # slope of the SVAP-temperature curve (mbar/Celsius);
    # measured vapour pressure not to exceed saturated vapour pressure

    SVAP = 6.10588 * exp(17.32491 * TMPA / (TMPA + 238.102))
    DELTA = 238.102 * 17.32491 * SVAP / (TMPA + 238.102) ** 2
    VAP = min(VAP, SVAP)

    # the expression n/N (RELSSD) from the Penman formula is estimated
    # from the Angstrom formula: RI=RA(A+B.n/N) -> n/N=(RI/RA-A)/B,
    # where RI/RA is the atmospheric transmission obtained by a CALL
    # to ASTRO:

    RELSSD = limit(0., 1., (ATMTR - abs(ANGSTA)) / abs(ANGSTB))

    # Terms in Penman formula, for water, soil and canopy

    # net outgoing long-wave radiation (J/m2/d) acc. to Brunt (1932)
    RB = STBC * (TMPA + 273.) ** 4 * (0.56 - 0.079 * sqrt(VAP)) * (0.1 + 0.9 * RELSSD)

    # net absorbed radiation, expressed in mm/d
    RNW = (AVRAD * (1. - REFCFW) - RB) / LHVAP
    RNS = (AVRAD * (1. - REFCFS) - RB) / LHVAP
    RNC = (AVRAD * (1. - REFCFC) - RB) / LHVAP

    # evaporative demand of the atmosphere (mm/d)
    EA = 0.26 * max(0., (SVAP - VAP)) * (0.5 + BU * WIND2)
    EAC = 0.26 * max(0., (SVAP - VAP)) * (1.0 + BU * WIND2)

    # Penman formula (1948)
    E0 = (DELTA * RNW + GAMMA * EA) / (DELTA + GAMMA)
    ES0 = (DELTA * RNS + GAMMA * EA) / (DELTA + GAMMA)
    ET0 = (DELTA * RNC + GAMMA * EAC) / (DELTA + GAMMA)

    # Ensure reference evaporation >= 0.
    E0 = max(0., E0)
    ES0 = max(0., ES0)
    ET0 = max(0., ET0)

    return E0, ES0, ET0


def penman_monteith(DAY, LAT, ELEV, TMIN, TMAX, AVRAD, VAP, WIND2, ANGOT):
    """Calculates reference ET0 based on the Penman-Monteith model.

     This routine calculates the potential evapotranspiration rate from
     a reference crop canopy (ET0) in mm/d. For these calculations the
     analysis by FAO is followed as laid down in the FAO publication
     `Guidelines for computing crop water requirements - FAO Irrigation
     and drainage paper 56 <http://www.fao.org/docrep/X0490E/x0490e00.htm#Contents>`_

    Input variables::

        DAY   -  Python datetime.date object                   -
        LAT   -  Latitude of the site                        degrees
        ELEV  - Elevation above sea level                      m
        TMIN  - Minimum temperature                            C
        TMAX  - Maximum temperature                            C
        AVRAD - Daily shortwave radiation                   J m-2 d-1
        VAP   - 24 hour average vapour pressure               hPa
        WIND2 - 24 hour average windspeed at 2 meter          m/s

    Output is:

        ET0   - Penman-Monteith potential transpiration
                rate from a crop canopy                     [mm/d]
    """

    # psychrometric instrument constant (kPa/Celsius)
    PSYCON = 0.665
    # albedo and surface resistance [sec/m] for the reference crop canopy
    REFCFC = 0.23;
    CRES = 70.
    # latent heat of evaporation of water [J/kg == J/mm] and
    LHVAP = 2.45E6
    # Stefan Boltzmann constant (J/m2/d/K4, e.g multiplied by 24*60*60)
    STBC = 4.903E-3
    # Soil heat flux [J/m2/day] explicitly set to zero
    G = 0.

    # mean daily temperature (Celsius)
    TMPA = (TMIN + TMAX) / 2.

    # Vapour pressure to kPa
    VAP = hPa2kPa(VAP)

    # atmospheric pressure (kPa)
    T = Celsius2Kelvin(TMPA)
    PATM = 101.3 * pow((T - (0.0065 * ELEV)) / T, 5.26)

    # psychrometric constant (kPa/Celsius)
    GAMMA = PSYCON * PATM * 1.0E-3

    # Derivative of SVAP with respect to mean temperature, i.e.
    # slope of the SVAP-temperature curve (kPa/Celsius);
    SVAP_TMPA = SatVapourPressure(TMPA)
    DELTA = (4098. * SVAP_TMPA) / pow((TMPA + 237.3), 2)

    # Daily average saturated vapour pressure [kPa] from min/max temperature
    SVAP_TMAX = SatVapourPressure(TMAX)
    SVAP_TMIN = SatVapourPressure(TMIN)
    SVAP = (SVAP_TMAX + SVAP_TMIN) / 2.

    # measured vapour pressure not to exceed saturated vapour pressure
    VAP = min(VAP, SVAP)

    # Longwave radiation according at Tmax, Tmin (J/m2/d)
    # and preliminary net outgoing long-wave radiation (J/m2/d)
    STB_TMAX = STBC * pow(Celsius2Kelvin(TMAX), 4)
    STB_TMIN = STBC * pow(Celsius2Kelvin(TMIN), 4)
    RNL_TMP = ((STB_TMAX + STB_TMIN) / 2.) * (0.34 - 0.14 * sqrt(VAP))

    # Clear Sky radiation [J/m2/DAY] from Angot TOA radiation
    # the latter is found through a call to astro()

    CSKYRAD = (0.75 + (2e-05 * ELEV)) * ANGOT

    if CSKYRAD > 0:
        # Final net outgoing longwave radiation [J/m2/day]
        RNL = RNL_TMP * (1.35 * (AVRAD / CSKYRAD) - 0.35)

        # radiative evaporation equivalent for the reference surface
        # [mm/DAY]
        RN = ((1 - REFCFC) * AVRAD - RNL) / LHVAP

        # aerodynamic evaporation equivalent [mm/day]
        EA = ((900. / (TMPA + 273)) * WIND2 * (SVAP - VAP))

        # Modified psychometric constant (gamma*)[kPa/C]
        MGAMMA = GAMMA * (1. + (CRES / 208. * WIND2))

        # Reference ET in mm/day
        ET0 = (DELTA * (RN - G)) / (DELTA + MGAMMA) + (GAMMA * EA) / (DELTA + MGAMMA)
        ET0 = max(0., ET0)
    else:
        ET0 = 0.

    return ET0


def doy(day):
    """Converts a date or datetime object to day-of-year (Jan 1st = doy 1)
    """
    # Check if day is a date or datetime object
    if isinstance(day, (datetime.date, datetime.datetime)):
        return day.timetuple().tm_yday
    else:
        msg = "Parameter day is not a date or datetime object."
        raise RuntimeError(msg)
