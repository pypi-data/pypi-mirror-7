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

from . import sixs
from .Params import *
from pylab import *
import numpy as np


def all_angles(s):
    azimuths = np.linspace(0, 360, 30)
    zeniths = np.arange(0, 70, 10)
    values = []

    for azimuth in azimuths:
        for zenith in zeniths:
            # Run some sort of model and get some output
            # We'll just use rand for this example
            s.geometry.view_a = azimuth
            s.geometry.view_z = zenith
            s.run()
            # values.append(s.outputs.pixel_reflectance)
            d = dict(s.outputs.values)
            values.append(d)
            print "%i %i %f" % (azimuth, zenith, d['pixel_reflectance'])

    return values


def plot_all_angles(values):
    azimuths = np.linspace(0, 360, 30)
    zeniths = np.arange(0, 70, 10)
    theta = np.radians(azimuths)

    #values = [getattr(item, 'pixel_reflectance') for item in values]
    values = [item['pixel_reflectance'] for item in values]

    values = np.array(values)
    values = values.reshape(len(azimuths), len(zeniths))

    r, theta = np.meshgrid(zeniths, np.radians(azimuths))
    fig, ax = subplots(subplot_kw=dict(projection='polar'))
    ax.contourf(theta, r, values)
    autumn()
    show()

if __name__ == '__main__':
    # Create the 6S object
    s = sixs.SixS()

    # Set some parameters
    s.ground_reflectance = GroundReflectance.HomogeneousRoujean(0.037, 0.0, 0.133)
    s.solar_z = 30
    s.solar_a = 0

    v = all_angles(s)

    plot_all_angles(v)
