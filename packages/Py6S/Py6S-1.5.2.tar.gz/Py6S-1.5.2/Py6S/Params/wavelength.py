# This file is part of Py6S.
#
# Copyright 2012 Robin Wilson and contributors listed in the CONTRIBUTORS file.
#
# Py6S is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Py6S is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Py6S.  If not, see <http://www.gnu.org/licenses/>.

from .. import sixs_exceptions
import collections
import numpy as np


def Wavelength(start_wavelength, end_wavelength=None, filter=None):
    """Select one or more wavelengths for the 6S simulation.

    There are a number of ways to do this:

    1. Pass a single value of a wavelength in micrometres. The simulation will be performed for just this wavelength::

        Wavelength(0.43)

    2. Pass a start and end wavelength in micrometres. The simulation will be performed across this wavelength range with a constant filter function (spectral response function) of 1.0::

        Wavelength(0.43, 0.50)

    3. Pass a start and end wavelength, and a filter given at 2.5nm intervals. The simulation will be performed across this wavelength range using the given filter function::

        Wavelength(0.400, 0.410, [0.7, 0.9, 1.0, 0.3])

    4. Pass a constant (as defined in this class) for a pre-defined wavelength range::

        Wavelength(PredefinedWavelengths.LANDSAT_TM_B1)

    """
    try:
        wv_id = start_wavelength[0]
        if wv_id > 0:
            # It's one of the new predefined wavelengths that I've added
            return Wavelength(start_wavelength[1], start_wavelength[2], start_wavelength[3])
        else:
            wv_type = "%d (Chosen Band)\n" % (-1 * wv_id)
            data = None
            min_wv = start_wavelength[1]
            max_wv = start_wavelength[2]
    except:
        if end_wavelength is None:
            # It's simply a wavelength value
            if start_wavelength > PredefinedWavelengths.MAX_ALLOWABLE_WAVELENGTH or start_wavelength < PredefinedWavelengths.MIN_ALLOWABLE_WAVELENGTH:
                raise sixs_exceptions.ParameterError("wavelength", "Wavelength must be between %f and %f" % (PredefinedWavelengths.MIN_ALLOWABLE_WAVELENGTH, PredefinedWavelengths.MAX_ALLOWABLE_WAVELENGTH))
            wv_type = "-1"
            data = "%f" % start_wavelength
            min_wv = start_wavelength
            max_wv = start_wavelength
        else:
            if start_wavelength > PredefinedWavelengths.MAX_ALLOWABLE_WAVELENGTH or start_wavelength < PredefinedWavelengths.MIN_ALLOWABLE_WAVELENGTH or end_wavelength > PredefinedWavelengths.MAX_ALLOWABLE_WAVELENGTH or end_wavelength < PredefinedWavelengths.MIN_ALLOWABLE_WAVELENGTH:
                raise sixs_exceptions.ParameterError("wavelength", "Wavelength must be between %f and %f" % (PredefinedWavelengths.MIN_ALLOWABLE_WAVELENGTH, PredefinedWavelengths.MAX_ALLOWABLE_WAVELENGTH))
            min_wv = start_wavelength
            max_wv = end_wavelength
            if filter is None:
                # They haven't given a filter, so assume filter is constant at 1
                wv_type = "0 constant filter function"
                data = "%f %f" % (start_wavelength, end_wavelength)
            else:
                # Filter has been given, so we must use it.
                # We assume filter has been given at 2.5nm intervals
                wv_type = "1 User's defined filtered function"
                data = """%f %f
    %s""" % (start_wavelength, end_wavelength, " ".join(map(str, filter)))

    if data is None:
        return_string = wv_type
    else:
        return_string =  """%s
%s\n""" % (wv_type, data)

    return (return_string, min_wv, max_wv)


class PredefinedWavelengths:
    MAX_ALLOWABLE_WAVELENGTH = 4
    MIN_ALLOWABLE_WAVELENGTH = 0.2

    # New predefined wavelengths that I've added to Py6S
    # CONSTANT_NAME = (ID, Start Wavelength, End Wavelength, Filter Function)
    # Note: IDs must be > 1 for new predefined wavelengths

    # Landsat OLI
    # Taken from spreadsheet downloadable from http://landsat.gsfc.nasa.gov/?p=5779
    # Interpolated to 2.5nm intervals, as required by 6S
    LANDSAT_OLI_B1 = (1, 0.427, 0.457,
                      np.array([7.30000000e-05, 2.52450000e-03, 2.47670000e-02,
                                3.85985000e-01, 9.08749000e-01, 9.80591500e-01,
                                9.86713000e-01, 9.96568500e-01, 9.82780000e-01,
                                8.25707000e-01, 2.26412000e-01, 2.55700000e-02,
                                2.41400000e-03]))

    LANDSAT_OLI_B2 = (2, 0.436, 0.526,
                      np.array([1.00000000e-05, 1.79000000e-04, 4.55000000e-04,
                                1.63350000e-03, 6.86900000e-03, 4.28880000e-02,
                                2.71370000e-01, 7.90740500e-01, 9.03034000e-01,
                                9.04677500e-01, 8.89667000e-01, 8.79232000e-01,
                                8.79688000e-01, 8.89796500e-01, 8.48533000e-01,
                                8.36270500e-01, 8.68497000e-01, 9.11461500e-01,
                                9.31726000e-01, 9.54896500e-01, 9.56424000e-01,
                                9.83834000e-01, 9.89469000e-01, 9.68066500e-01,
                                9.88729000e-01, 9.61057500e-01, 9.66125000e-01,
                                9.82077000e-01, 9.63135000e-01, 9.98249000e-01,
                                8.44893000e-01, 1.19533500e-01, 5.32800000e-03,
                                1.32850000e-03, 5.16000000e-04, 1.17000000e-04,
                                2.30000000e-05]))

    LANDSAT_OLI_B3 = (3, 0.512, 0.610,
                      np.array([-4.60000000e-05, 1.78500000e-04, 6.48000000e-04,
                                1.57400000e-03, 3.44600000e-03, 8.73250000e-03,
                                2.55130000e-02, 9.69975000e-02, 3.53885000e-01,
                                8.03215000e-01, 9.54627000e-01, 9.60271500e-01,
                                9.69873000e-01, 9.69833500e-01, 9.77001000e-01,
                                9.95392000e-01, 9.82642000e-01, 9.71423000e-01,
                                9.46245000e-01, 9.62786000e-01, 9.66447000e-01,
                                9.64176500e-01, 9.83397000e-01, 9.70875500e-01,
                                9.78208000e-01, 9.77182500e-01, 9.69181000e-01,
                                9.81277000e-01, 9.68886000e-01, 9.80432000e-01,
                                9.04478000e-01, 6.05139000e-01, 1.90467000e-01,
                                2.47350000e-02, 2.57400000e-03, 2.39500000e-04,
                                0, 0, 0,
                                0]))

    LANDSAT_OLI_B4 = (4, 0.625, 0.690,
                      np.array([-3.42000000e-04, 1.37250000e-03, 7.19700000e-03,
                                4.86465000e-02, 2.99778000e-01, 8.34958000e-01,
                                9.50823000e-01, 9.57268000e-01, 9.84173000e-01,
                                9.83172500e-01, 9.59441000e-01, 9.54442500e-01,
                                9.81688000e-01, 9.88501500e-01, 9.76960000e-01,
                                9.88942000e-01, 9.80678000e-01, 9.66466000e-01,
                                9.66928000e-01, 7.29107000e-01, 1.23946000e-01,
                                1.25175000e-02, 1.40200000e-03, 0,
                                0, 0, 0]))

    LANDSAT_OLI_B5 = (5, 0.829, 0.899,
                      np.array([0, 7.50000000e-05, 3.14000000e-04,
                                8.52500000e-04, 2.10700000e-03, 5.90150000e-03,
                                1.73460000e-02, 6.62770000e-02, 2.49733000e-01,
                                6.63830000e-01, 9.60215000e-01, 9.76869500e-01,
                                1.00000000e+00, 9.78334000e-01, 9.57357000e-01,
                                9.50103000e-01, 9.48450000e-01, 9.53355500e-01,
                                9.69821000e-01, 8.39899500e-01, 4.48364000e-01,
                                1.37481000e-01, 3.45320000e-02, 1.00205000e-02,
                                2.94400000e-03, 9.67500000e-04, 2.41000000e-04,
                                1.55000000e-05, 0]))

    LANDSAT_OLI_B6 = (6, 1.340, 1.407,
                      np.array([0, 2.57500000e-04, 6.47000000e-04,
                                1.27400000e-03, 2.31800000e-03, 4.70450000e-03,
                                1.11240000e-02, 3.45385000e-02, 1.15351000e-01,
                                3.86681500e-01, 7.72118000e-01, 9.00941500e-01,
                                9.31247000e-01, 9.91687000e-01, 1.00000000e+00,
                                9.77080500e-01, 8.71343000e-01, 6.54888000e-01,
                                2.97920000e-01, 8.96145000e-02, 2.60840000e-02,
                                8.30650000e-03, 2.78000000e-03, 1.11900000e-03,
                                2.20000000e-04, 0, 0,
                                0]))

    LANDSAT_OLI_B7 = (7, 1.515, 1.695,
                      np.array([0, 2.00000000e-04, 4.66000000e-04,
                                8.45000000e-04, 1.36900000e-03, 2.01550000e-03,
                                2.88100000e-03, 4.02150000e-03, 5.52800000e-03,
                                7.88900000e-03, 1.09890000e-02, 1.52755000e-02,
                                2.18310000e-02, 3.25615000e-02, 4.78640000e-02,
                                7.09490000e-02, 1.01893000e-01, 1.50884500e-01,
                                2.20261000e-01, 3.10649000e-01, 4.21470000e-01,
                                5.52234000e-01, 6.76683000e-01, 7.71509000e-01,
                                8.54065000e-01, 8.95823500e-01, 9.13009000e-01,
                                9.25058000e-01, 9.26413000e-01, 9.23818000e-01,
                                9.22828000e-01, 9.22408500e-01, 9.26605000e-01,
                                9.43438000e-01, 9.46175000e-01, 9.47297500e-01,
                                9.52859000e-01, 9.51358500e-01, 9.59047000e-01,
                                9.59191500e-01, 9.61470000e-01, 9.60494000e-01,
                                9.64703000e-01, 9.69951500e-01, 9.76906000e-01,
                                9.81271500e-01, 9.88609000e-01, 9.99010500e-01,
                                9.99642000e-01, 9.89828000e-01, 9.67125000e-01,
                                9.26719000e-01, 8.40967000e-01, 7.23103000e-01,
                                5.73232000e-01, 4.22998000e-01, 2.91752000e-01,
                                1.95988000e-01, 1.28463000e-01, 8.28380000e-02,
                                5.27520000e-02, 3.45655000e-02, 2.25040000e-02,
                                1.47195000e-02, 9.58700000e-03, 6.39600000e-03,
                                4.25700000e-03, 2.79800000e-03, 1.78100000e-03,
                                1.14200000e-03, 6.77000000e-04, 3.55000000e-04,
                                1.12000000e-04]))

    LANDSAT_OLI_B7 = (8, 2.037, 2.354,
                      np.array([0, 1.07000000e-04, 2.40000000e-04,
                                3.99000000e-04, 5.99000000e-04, 8.80500000e-04,
                                1.22200000e-03, 1.64550000e-03, 2.18700000e-03,
                                2.85300000e-03, 3.73300000e-03, 4.88200000e-03,
                                6.33700000e-03, 8.44950000e-03, 1.10050000e-02,
                                1.42985000e-02, 1.88990000e-02, 2.45090000e-02,
                                3.20710000e-02, 4.28190000e-02, 5.64290000e-02,
                                7.48955000e-02, 1.00640000e-01, 1.36480000e-01,
                                1.79714000e-01, 2.40483000e-01, 3.11347000e-01,
                                3.94832500e-01, 4.88816000e-01, 5.73971000e-01,
                                6.63067000e-01, 7.39406500e-01, 7.92667000e-01,
                                8.41172500e-01, 8.67845000e-01, 8.86269000e-01,
                                9.06527000e-01, 9.14538000e-01, 9.29693000e-01,
                                9.38975000e-01, 9.42952000e-01, 9.44181000e-01,
                                9.48776000e-01, 9.49521500e-01, 9.56635000e-01,
                                9.48258500e-01, 9.50874000e-01, 9.47049500e-01,
                                9.57717000e-01, 9.47095000e-01, 9.51641000e-01,
                                9.46800000e-01, 9.40311000e-01, 9.46466500e-01,
                                9.38737000e-01, 9.44439000e-01, 9.44482000e-01,
                                9.50472000e-01, 9.39939000e-01, 9.37156500e-01,
                                9.38955000e-01, 9.28123500e-01, 9.30508000e-01,
                                9.30946000e-01, 9.36472000e-01, 9.34327500e-01,
                                9.46217000e-01, 9.53826000e-01, 9.63135000e-01,
                                9.63944000e-01, 9.62905000e-01, 9.61607000e-01,
                                9.57814000e-01, 9.55657500e-01, 9.51706000e-01,
                                9.60275500e-01, 9.47696000e-01, 9.59807000e-01,
                                9.55750000e-01, 9.56607500e-01, 9.66786000e-01,
                                9.62823000e-01, 9.77637000e-01, 9.83457500e-01,
                                9.85056000e-01, 9.98627000e-01, 9.92469000e-01,
                                9.97947000e-01, 9.97261000e-01, 9.89437000e-01,
                                9.86037000e-01, 9.81280000e-01, 9.72794000e-01,
                                9.76369500e-01, 9.74409000e-01, 9.63698500e-01,
                                9.55095000e-01, 9.51391500e-01, 9.22405000e-01,
                                8.89264000e-01, 8.23876000e-01, 7.21272500e-01,
                                6.02539000e-01, 4.77695500e-01, 3.55569000e-01,
                                2.61452500e-01, 1.86151000e-01, 1.31725000e-01,
                                9.20290000e-02, 6.49895000e-02, 4.63320000e-02,
                                3.34235000e-02, 2.40000000e-02, 1.76250000e-02,
                                1.29300000e-02, 9.55700000e-03, 7.08800000e-03,
                                5.33100000e-03, 3.90300000e-03, 2.83800000e-03,
                                2.04700000e-03, 1.44950000e-03, 9.74000000e-04,
                                6.20000000e-04, 3.20000000e-04, 7.35000000e-05,
                                0, 0]))

    LANDSAT_OLI_PAN = (9, 0.488, 0.691,
                       np.array([2.16000000e-04, 1.30000000e-03, 3.84100000e-03,
                                 1.22590000e-02, 4.27230000e-02, 1.60137500e-01,
                                 4.72496000e-01, 7.45412500e-01, 8.31881000e-01,
                                 8.55321500e-01, 8.59640000e-01, 8.57696000e-01,
                                 8.58455000e-01, 8.58301000e-01, 8.50183000e-01,
                                 8.58223500e-01, 8.61508000e-01, 8.57683500e-01,
                                 8.79249000e-01, 8.91710500e-01, 9.06294000e-01,
                                 9.12867000e-01, 9.02939000e-01, 9.20739500e-01,
                                 9.13020000e-01, 8.85650500e-01, 8.79443000e-01,
                                 8.74179000e-01, 8.75361000e-01, 8.91665000e-01,
                                 8.74097000e-01, 8.86888500e-01, 9.03528000e-01,
                                 9.10950500e-01, 9.13190000e-01, 9.20178000e-01,
                                 9.24431000e-01, 9.29809500e-01, 9.48863000e-01,
                                 9.40543000e-01, 9.45674000e-01, 9.39380000e-01,
                                 9.46659000e-01, 9.34044500e-01, 9.40838000e-01,
                                 9.58039500e-01, 9.68241000e-01, 9.66480500e-01,
                                 9.57232000e-01, 9.47675500e-01, 9.52465000e-01,
                                 9.57481500e-01, 9.64158000e-01, 9.67366000e-01,
                                 9.77026000e-01, 9.76029500e-01, 9.69583000e-01,
                                 9.72807000e-01, 9.65780000e-01, 9.66738000e-01,
                                 9.72067000e-01, 9.79346500e-01, 9.71123000e-01,
                                 9.53377000e-01, 9.63851000e-01, 9.67101500e-01,
                                 9.70613000e-01, 9.79974500e-01, 9.88302000e-01,
                                 9.91753000e-01, 1.00000000e+00, 9.98476000e-01,
                                 9.92555000e-01, 9.85811500e-01, 9.13945000e-01,
                                 5.24376500e-01, 1.67313000e-01, 4.61755000e-02,
                                 1.51780000e-02, 6.70950000e-03, 3.22000000e-03,
                                 1.21200000e-03]))

    # All of the original predefined wavelengths from 6S
    # CONSTANT_NAME = (ID for Constant, Start Wavelength, End Wavelength)
    METEOSAT_VISIBLE = (-2, 0.35, 1.11)
    GOES_EAST_VISIBLE = (-3, 0.49, 0.9)
    GOES_WEST_VISIBLE = (-4, 0.49, 0.9)
    AVHRR_NOAA6_B1 = (-5, 0.55, 0.75)
    AVHRR_NOAA6_B2 = (-6, 0.69, 1.12)
    AVHRR_NOAA7_B1 = (-7, 0.5, 0.8)
    AVHRR_NOAA7_B2 = (-8, 0.64, 1.17)
    AVHRR_NOAA8_B1 = (-9, 0.54, 1.01)
    AVHRR_NOAA8_B2 = (-10, 0.68, 1.12)
    AVHRR_NOAA9_B1 = (-11, 0.53, 0.81)
    AVHRR_NOAA9_B2 = (-12, 0.68, 1.17)
    AVHRR_NOAA10_B1 = (-13, 0.53, 0.78)
    AVHRR_NOAA10_B2 = (-14, 0.6, 1.19)
    AVHRR_NOAA11_B1 = (-15, 0.54, 0.82)
    AVHRR_NOAA11_B2 = (-16, 0.6, 1.12)
    SPOT_HRV1_B1 = (-17, 0.47, 0.65)
    SPOT_HRV1_B2 = (-18, 0.6, 0.72)
    SPOT_HRV1_B3 = (-19, 0.73, 0.93)
    SPOT_HRV1_PAN = (-20, 0.47, 0.79)
    SPOT_HRV2_B1 = (-21, 0.47, 0.65)
    SPOT_HRV2_B2 = (-22, 0.59, 0.73)
    SPOT_HRV2_B3 = (-23, 0.74, 0.94)
    SPOT_HRV2_PAN = (-24, 0.47, 0.79)
    LANDSAT_TM_B1 = (-25, 0.43, 0.56)
    LANDSAT_TM_B2 = (-26, 0.5, 0.65)
    LANDSAT_TM_B3 = (-27, 0.58, 0.74)
    LANDSAT_TM_B4 = (-28, 0.73, 0.95)
    LANDSAT_TM_B5 = (-29, 1.5025, 1.89)
    LANDSAT_TM_B7 = (-30, 1.95, 2.41)
    LANDSAT_MSS_B1 = (-31, 0.475, 0.64)
    LANDSAT_MSS_B2 = (-32, 0.58, 0.75)
    LANDSAT_MSS_B3 = (-33, 0.655, 0.855)
    LANDSAT_MSS_B4 = (-34, 0.785, 1.1)
    ER2_MAS_B1 = (-35, 0.5025, 0.5875)
    ER2_MAS_B2 = (-36, 0.6075, 0.7)
    ER2_MAS_B3 = (-37, 0.83, 0.9125)
    ER2_MAS_B4 = (-38, 0.9, 0.9975)
    ER2_MAS_B5 = (-39, 1.82, 1.9575)
    ER2_MAS_B6 = (-40, 2.0950, 2.1925)
    ER2_MAS_B7 = (-41, 3.58, 3.87)
    MODIS_B1 = (-42, 0.61, 0.685)
    MODIS_B2 = (-43, 0.82, 0.9025)
    MODIS_B3 = (-44, 0.45, 0.4825)
    MODIS_B4 = (-45, 0.54, 0.57)
    MODIS_B5 = (-46, 1.2150, 1.27)
    MODIS_B6 = (-47, 1.6, 1.665)
    MODIS_B7 = (-48, 2.0575, 2.1825)
    MODIS_B8 = (-49, 0.4025, 0.4225)
    AVHRR_NOAA12_B1 = (-50, 0.5, 1.0)
    AVHRR_NOAA12_B2 = (-51, 0.65, 1.12)
    AVHRR_NOAA14_B1 = (-52, 0.5, 1.11)
    AVHRR_NOAA14_B2 = (-53, 0.68, 1.1)
    POLDER_B1 = (-54, 0.4125, 0.4775)
    POLDER_B2 = (-55, 0.41, 0.5225)
    POLDER_B3 = (-56, 0.5325, 0.595)
    POLDER_B4 = (-57, 0.63, 0.7025)
    POLDER_B5 = (-58, 0.745, 0.78)
    POLDER_B6 = (-59, 0.7, 0.83)
    POLDER_B7 = (-60, 0.81, 0.92)
    POLDER_B8 = (-61, 0.8650, 0.94)
    SEAWIFS_B1 = (-62, 0.3825, 0.7)
    SEAWIFS_B2 = (-63, 0.38, 0.58)
    SEAWIFS_B3 = (-64, 0.38, 1.02)
    SEAWIFS_B4 = (-65, 0.38, 1.02)
    SEAWIFS_B5 = (-66, 0.3825, 1.15)
    SEAWIFS_B6 = (-67, 0.3825, 1.05)
    SEAWIFS_B7 = (-68, 0.38, 1.15)
    SEAWIFS_B8 = (-69, 0.38, 1.15)
    AATSR_B1 = (-70, 0.525, 0.5925)
    AATSR_B2 = (-71, 0.6275, 0.6975)
    AATSR_B3 = (-72, 0.8325, 0.9025)
    AATSR_B4 = (-73, 1.4475, 1.7775)
    MERIS_B1 = (-74, 0.412, 0.412 + 0.00998)
    MERIS_B2 = (-75, 0.442, 0.442 + 0.00997)
    MERIS_B3 = (-76, 0.489, 0.489 + 0.00997)
    MERIS_B4 = (-77, 0.509, 0.509 + 0.00997)
    MERIS_B5 = (-78, 0.559, 0.559 + 0.00997)
    MERIS_B6 = (-79, 0.619, 0.619 + 0.00997)
    MERIS_B7 = (-80, 0.664, 0.664 + 0.00998)
    MERIS_B8 = (-81, 0.681, 0.681 + 0.00749)
    MERIS_B9 = (-82, 0.708, 0.708 + 0.00999)
    MERIS_B10 = (-83, 0.753, 0.753 + 0.00749)
    MERIS_B11 = (-84, 0.760, 0.760 + 0.00374)
    MERIS_B12 = (-85, 0.778, 0.778 + 0.00150)
    MERIS_B13 = (-86, 0.865, 0.865 + 0.002)
    MERIS_B14 = (-87, 0.885, 0.885 + 0.001)
    MERIS_B15 = (-88, 0.9, 0.9 + 0.001)
    GLI_B1 = (-89, 0.37, 0.3925)
    GLI_B2 = (-90, 0.3875, 0.4125)
    GLI_B3 = (-91, 0.3975, 0.4275)
    GLI_B4 = (-92, 0.4475, 0.505)
    GLI_B5 = (-93, 0.4475, 0.46)
    GLI_B6 = (-94, 0.475, 0.505)
    GLI_B7 = (-95, 0.5075, 0.5325)
    GLI_B8 = (-96, 0.5265, 0.56)
    GLI_B9 = (-97, 0.5475, 0.5825)
    GLI_B10 = (-98, 0.61, 0.64)
    GLI_B11 = (-99, 0.6525, 0.6825)
    GLI_B12 = (-100, 0.665, 0.695)
    GLI_B13 = (-101, 0.6625, 0.6975)
    GLI_B14 = (-102, 0.6925, 0.7275)
    GLI_B15 = (-103, 0.6925, 0.7275)
    GLI_B16 = (-104, 0.7325, 0.7675)
    GLI_B17 = (-105, 0.75, 0.775)
    GLI_B18 = (-106, 0.84, 0.8925)
    GLI_B19 = (-107, 0.85, 0.88)
    GLI_B20 = (-108, 0.415, 0.5075)
    GLI_B21 = (-109, 0.505, 0.58)
    GLI_B22 = (-110, 0.6075, 0.715)
    GLI_B23 = (-111, 0.745, 0.9075)
    GLI_B24 = (-112, 1.03, 1.07)
    GLI_B25 = (-113, 1.085, 1.19)
    GLI_B26 = (-114, 1.22, 1.2625)
    GLI_B27 = (-115, 1.3475, 1.415)
    GLI_B28 = (-116, 1.515, 1.77)
    GLI_B29 = (-117, 2.055, 2.345)
    GLI_B30 = (-118, 3.22, 4.0)
    ALI_B1P = (-119, 0.4225, 0.4625)
    ALI_B1 = (-120, 0.4325, 0.550)
    ALI_B2 = (-121, 0.5, 0.63)
    ALI_B3 = (-122, 0.5775, 0.750)
    ALI_B4 = (-123, 0.7525, 0.8375)
    ALI_B4P = (-124, 0.8025, 0.935)
    ALI_B5P = (-125, 1.130, 1.345)
    ALI_B5 = (-126, 1.47, 1.820)
    ALI_B7 = (-127, 1.98, 2.53)
    ASTER_B1 = (-128, 0.485, 0.6425)
    ASTER_B2 = (-129, 0.590, 0.730)
    ASTER_B3N = (-130, 0.720, 0.9075)
    ASTER_B3B = (-131, 0.720, 0.9225)
    ASTER_B4 = (-132, 1.57, 1.7675)
    ASTER_B5 = (-133, 2.120, 2.2825)
    ASTER_B6 = (-134, 2.150, 2.295)
    ASTER_B7 = (-135, 2.210, 2.39)
    ASTER_B8 = (-136, 2.250, 2.244)
    ASTER_B9 = (-137, 2.2975, 2.4875)
    LANDSAT_ETM_B1 = (-138, 0.435, 0.52)
    LANDSAT_ETM_B2 = (-139, 0.5, 0.6225)
    LANDSAT_ETM_B3 = (-140, 0.615, 0.7025)
    LANDSAT_ETM_B4 = (-141, 0.74, 0.9125)
    LANDSAT_ETM_B5 = (-142, 1.51, 1.7875)
    LANDSAT_ETM_B7 = (-143, 2.015, 2.3775)
    HYPBLUE_B1 = (-144, 0.4375, 0.5)
    HYPBLUE_B2 = (-145, 0.435, 0.52)
    SPOT_VGT_B1 = (-146, 0.4175, 0.5)
    SPOT_VGT_B2 = (-147, 0.5975, 0.7675)
    SPOT_VGT_B3 = (-148, 0.7325, 0.9575)
    SPOT_VGT_B4 = (-149, 1.5225, 1.8)
    VIIRS_BM1 = (-150, 0.4025, 0.4225)
    VIIRS_BM2 = (-151, 0.4350, 0.4550)
    VIIRS_BM3 = (-152, 0.4775, 0.4975)
    VIIRS_BM4 = (-153, 0.5450, 0.565)
    VIIRS_BM5 = (-154, 0.6625, 0.6825)
    VIIRS_BM6 = (-155, 0.7375, 0.7525)
    VIIRS_BM7 = (-156, 0.8450, 0.8850)
    VIIRS_BM8 = (-157, 1.23, 1.25)
    VIIRS_BM9 = (-158, 1.37, 1.385)
    VIIRS_BM10 = (-159, 1.58, 1.64)
    VIIRS_BM11 = (-160, 2.225, 2.275)
    VIIRS_BM12 = (-161, 3.61, 3.79)
    VIIRS_BI1 = (-162, 0.6, 0.68)
    VIIRS_BI2 = (-163, 0.845, 0.885)
    VIIRS_BI3 = (-164, 1.58, 1.64)
    VIIRS_BI4 = (-165, 3.55, 3.93)
