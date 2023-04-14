# -*- coding: utf-8 -*-
# This component is derived from PCSE software/Wofost model
# (Copyright @ 2004-2014 Alterra, Wageningen-UR; Allard de Wit allard.dewit@wur.nl, April 2014)
# and modified by EC-JRC for the eCrops framework under the European Union Public License (EUPL), Version 1.2
# European Commission, Joint Research Centre, March 2023


from math import cos, sin, asin, sqrt, exp
from ..Printable import Printable

class Astro:
    """This class contains functions to calculate astronomic variables"""


    def calc_astro(self,status):
        """python version of ASTRO routine by Daniel van Kraalingen.

        This subroutine calculates astronomic daylength, diurnal radiation
        characteristics such as the atmospheric transmission, diffuse radiation etc.

        Input data:
         - day:         date/datetime object
         - latitude:    latitude of location
         - radiation:   daily global incoming radiation (J/m2/day)

        output is a `namedtuple` in the following order and tags::

            DAYL      Astronomical daylength (base = 0 degrees)     h
            DAYLP     Astronomical daylength (base =-4 degrees)     h
            SINLD     Seasonal offset of sine of solar height       -
            COSLD     Amplitude of sine of solar height             -
            DIFPP     Diffuse irradiation perpendicular to
                      direction of light                         J m-2 s-1
            ATMTR     Daily atmospheric transmission                -
            DSINBE    Daily total of effective solar height         s
            ANGOT     Angot radiation at top of atmosphere       J m-2 d-1

        Authors: Daniel van Kraalingen
        Date   : April 1991

        Python version
        Author      : Allard de Wit
        Date        : January 2011
        """
        # Check for range of latitude
        if abs(status.LAT) > 90.:
            msg = "Latitude not between -90 and 90"
            raise RuntimeError(msg)
        LAT = status.LAT

        # Determine day-of-year (IDAY) from day
        IDAY = status.doy

        # reassign radiation
        AVRAD = status.weather.IRRAD

        # constants
        RAD = 0.0174533
        PI = 3.1415926
        ANGLE = -4.

        # map python functions to capitals
        SIN = sin
        COS = cos
        ASIN = asin
        REAL = float
        SQRT = sqrt

        # Declination and solar constant for this day
        DEC = -ASIN(SIN(23.45 * RAD) * COS(2. * PI * (REAL(IDAY) + 10.) / 365.))
        SC = 1370. * (1. + 0.033 * COS(2. * PI * REAL(IDAY) / 365.))

        # calculation of daylength from intermediate variables
        # SINLD, COSLD and AOB
        SINLD = SIN(RAD * LAT) * SIN(DEC)
        COSLD = COS(RAD * LAT) * COS(DEC)
        AOB = SINLD / COSLD

        # For very high latitudes and days in summer and winter a limit is
        # inserted to avoid math errors when daylength reaches 24 hours in
        # summer or 0 hours in winter.

        # Calculate solution for base=0 degrees
        if abs(AOB) <= 1.0:
            DAYL = 12.0 * (1. + 2. * ASIN(AOB) / PI)
            # integrals of sine of solar height
            DSINB = 3600. * (DAYL * SINLD + 24. * COSLD * SQRT(1. - AOB ** 2) / PI)
            DSINBE = 3600. * (DAYL * (SINLD + 0.4 * (SINLD ** 2 + COSLD ** 2 * 0.5)) +
                              12. * COSLD * (2. + 3. * 0.4 * SINLD) * SQRT(1. - AOB ** 2) / PI)
        else:
            if AOB > 1.0: DAYL = 24.0
            if AOB < -1.0: DAYL = 0.0
            # integrals of sine of solar height
            DSINB = 3600. * (DAYL * SINLD)
            DSINBE = 3600. * (DAYL * (SINLD + 0.4 * (SINLD ** 2 + COSLD ** 2 * 0.5)))

        # Calculate solution for base=-4 (ANGLE) degrees
        AOB_CORR = (-SIN(ANGLE * RAD) + SINLD) / COSLD
        if abs(AOB_CORR) <= 1.0:
            DAYLP = 12.0 * (1. + 2. * ASIN(AOB_CORR) / PI)
        elif AOB_CORR > 1.0:
            DAYLP = 24.0
        elif AOB_CORR < -1.0:
            DAYLP = 0.0

        # extraterrestrial radiation and atmospheric transmission
        ANGOT = SC * DSINB
        # Check for DAYL=0 as in that case the angot radiation is 0 as well
        if DAYL > 0.0:
            ATMTR = AVRAD / ANGOT
        else:
            ATMTR = 0.

        # estimate fraction diffuse irradiation
        if (ATMTR > 0.75):
            FRDIF = 0.23
        elif (ATMTR <= 0.75) and (ATMTR > 0.35):
            FRDIF = 1.33 - 1.46 * ATMTR
        elif (ATMTR <= 0.35) and (ATMTR > 0.07):
            FRDIF = 1. - 2.3 * (ATMTR - 0.07) ** 2
        else:  # ATMTR <= 0.07
            FRDIF = 1.

        DIFPP = FRDIF * ATMTR * 0.5 * SC

        # return values in status variables, under astrodata root
        status.astrodata=Printable()
        status.astrodata.DAYL=DAYL
        status.astrodata.DAYLP=DAYLP
        status.astrodata.SINLD=SINLD
        status.astrodata.COSLD=COSLD
        status.astrodata.DIFPP=DIFPP
        status.astrodata.ATMTR=ATMTR
        status.astrodata.DSINBE=DSINBE
        status.astrodata.ANGOT=ANGOT
        return status
