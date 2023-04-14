# -*- coding: utf-8 -*-
# This component is derived from PCSE software/Wofost model
# (Copyright @ 2004-2014 Alterra, Wageningen-UR; Allard de Wit allard.dewit@wur.nl, April 2014)
# and modified by EC-JRC for the eCrops framework under the European Union Public License (EUPL), Version 1.2
# European Commission, Joint Research Centre, March 2023



"""AFGEN table implementation in ecrops. AFEGN tables are used to store functions as tables of X and Y"""

from bisect import bisect_left


def _check_x_ascending(tbl_xy):
    """Checks that the x values are strictly ascending.

    Also truncates any trailing (0.,0.) pairs as a results of data coming
    from a CGMS database.
    """
    if hasattr(tbl_xy, "__len__") is False or tbl_xy.__len__ == 1:
        return tbl_xy, 0
    x_list = list(tbl_xy)[0::2]
    y_list = list(tbl_xy)[1::2]
    n = len(x_list)

    # Check if x range is ascending continuously
    rng = list(range(1, n))
    x_asc = [True if (x_list[i] > x_list[i - 1]) else False for i in rng]

    # Check for breaks in the series where the ascending sequence stops.
    # Only 0 or 1 breaks are allowed. Use the XOR operator '^' here
    # n = len(x_asc)
    sum_break = sum([1 if (x0 ^ x1) else 0 for x0, x1 in zip(x_asc, x_asc[1:])])
    if sum_break == 0:
        x = x_list
        y = y_list
    elif sum_break == 1:
        x = [x_list[0]]
        y = [y_list[0]]
        for i, p in zip(rng, x_asc):
            if p is True:
                x.append(x_list[i])
                y.append(y_list[i])
    else:
        msg = ("X values for AFGEN input list not strictly ascending: %s"
               % x_list)
        raise ValueError(msg)

    return x, y


class Afgen(object):
    """Emulates the AFGEN function in WOFOST.

    :param tbl_xy: List or array of XY value pairs describing the function
        the X values should be mononically increasing.
    :param unit: The interpolated values is returned with given
        `unit <http://pypi.python.org/pypi/Unum/4.1.0>`_ assigned,
        defaults to None if Unum is not used.

    Returns the interpolated value provided with the
    absicca value at which the interpolation should take place.

    example::

        >>> tbl_xy = [0,0,1,1,5,10]
        >>> f =  Afgen(tbl_xy)
        >>> f(0.5)
        0.5
        >>> f(1.5)
        2.125
        >>> f(5)
        10.0
        >>> f(6)
        10.0
        >>> f(-1)
        0.0
    """

    def __init__(self, tbl_xy, unit=None):

        self.unit = unit

        x_list, y_list = _check_x_ascending(tbl_xy)
        if hasattr(x_list, "__len__") is False or x_list.__len__ == 1:
            return
        x_list = self.x_list = list(map(float, x_list))
        y_list = self.y_list = list(map(float, y_list))
        intervals = list(zip(x_list, x_list[1:], y_list, y_list[1:]))
        self.slopes = [(y2 - y1) / (x2 - x1) for x1, x2, y1, y2 in intervals]

    def __call__(self, x):

        if x <= self.x_list[0]:
            return self.y_list[0]
        if x >= self.x_list[-1]:
            return self.y_list[-1]

        i = bisect_left(self.x_list, x) - 1
        v = round(self.y_list[i] + self.slopes[i] * (x - self.x_list[i]),6)

        # if a unum unit is defined, multiply with a unit
        if self.unit is not None:
            v *= self.unit

        return v

    def toString(self):

        v="["
        i=0
        for x in self.x_list:
            v = v + "\n[" + str(x) + ","
            if len(self.y_list)>i:
                v = v + "" + str(self.y_list[i]) + "]"
            i=i+1

        v = v + "]"
        return v