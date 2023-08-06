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

import unittest
from Py6S import *
import numpy as np

class SimpleTests(unittest.TestCase):

  def test_inbuilt_test(self):
    result = SixS.test()
    self.assertEqual(result, 0)
    

class SixSClassTests(unittest.TestCase):

  def test_custom_path(self):
    s = SixS("/home/robintw/Py6S/6S/6SV1.1/sixsV1.1")
    s.run()

    self.assertAlmostEqual(s.outputs.transmittance_aerosol_scattering.downward, 0.93514, delta=0.002)

  def test_debug_report(self):
    s = SixS()
    s.produce_debug_report()

  # def test_not_on_path(self):
  #   import os

  #   old_path = os.environ["PATH"]
  #   os.environ["PATH"] = ""

  #   result = SixS.test()
  #   self.assertEqual(result, 1)

  #   os.environ["PATH"] = old_path
  #   print os.environ["PATH"]


class VisAOTTests(unittest.TestCase):

  def test_vis_aot_normal(self):
    s = SixS()
    s.run()
    
    self.assertAlmostEqual(s.outputs.visibility, 8.49, delta=0.002)
    self.assertAlmostEqual(s.outputs.aot550, 0.5, delta=0.002)
    
  def test_vis_aot_small(self):
    s = SixS()
    s.aot550 = 0.001
    s.run()
    
    self.assertAlmostEqual(s.outputs.visibility, float("Inf"))
    self.assertAlmostEqual(s.outputs.aot550, 0.001, delta=0.002)

  def test_set_vis(self):
    s = SixS()
    s.visibility = 40
    s.run()

    self.assertAlmostEqual(s.outputs.phase_function_Q.aerosol, -0.04939, delta=0.002)

class WavelengthTests(unittest.TestCase):

  def test_specific_wavelength(self):
    s = SixS()
    s.wavelength = Wavelength(0.567)
    s.run()
    
    self.assertAlmostEqual(s.outputs.apparent_radiance, 129.792, delta=0.002)
  
  def test_wavelength_range(self):
    s = SixS()
    s.wavelength = Wavelength(0.5, 0.7)
    s.run()
    
    self.assertAlmostEqual(s.outputs.apparent_radiance, 122.166, delta=0.002)
   
  def test_wavelength_filter(self):
    s = SixS()
    s.wavelength = Wavelength(0.400, 0.410, [0.7, 0.9, 1.0, 0.3, 1.0])
    s.run()
    
    self.assertAlmostEqual(s.outputs.apparent_radiance, 109.435, delta=0.002)
    
  def test_wavelength_predefined(self):
    s = SixS()
    s.wavelength = Wavelength(PredefinedWavelengths.LANDSAT_TM_B1)
    s.run()
    
    self.assertAlmostEqual(s.outputs.apparent_radiance, 138.126, delta=0.002)
    
    s.wavelength = Wavelength(PredefinedWavelengths.MODIS_B6)
    s.run()
    
    self.assertAlmostEqual(s.outputs.apparent_radiance, 17.917, delta=0.002)
    

  def test_invalid_wavelengths(self):
    with self.assertRaises(ParameterError):
      Wavelength(1000)

    with self.assertRaises(ParameterError):
      Wavelength(0.15)

    with self.assertRaises(ParameterError):
      Wavelength(0.5, 50)

class AtmosCorrTests(unittest.TestCase):

  def test_atmos_corr_radiance(self):
    s = SixS()
    s.atmos_corr = AtmosCorr.AtmosCorrLambertianFromRadiance(130.1)
    s.run()

    self.assertAlmostEqual(s.outputs.atmos_corrected_reflectance_lambertian, 0.29048, delta=0.002)

class UserDefinedSpectraTest(unittest.TestCase):

  def test_aster_spectra(self):
    s = SixS()
    s.ground_reflectance = GroundReflectance.HomogeneousLambertian(Spectra.import_from_aster("http://speclib.jpl.nasa.gov/speclibdata/jhu.becknic.water.ice.none.solid.ice.spectrum.txt"))
    s.run()
    
    self.assertAlmostEqual(s.outputs.apparent_radiance, 7.753, delta=0.002)

  def test_aster_spectra_from_file(self):
    s = SixS()
    s.altitudes.set_target_sea_level()
    s.altitudes.set_sensor_satellite_level()
    s.ground_reflectance = GroundReflectance.HomogeneousLambertian(Spectra.import_from_aster("./test/jhu.becknic.vegetation.trees.conifers.solid.conifer.spectrum.txt"))
    s.run()
    
    self.assertAlmostEqual(s.outputs.apparent_reflectance, 0.1403693, 0.002)

  def test_usgs_spectra(self):
    s = SixS()
    s.ground_reflectance = GroundReflectance.HomogeneousLambertian(Spectra.import_from_usgs("http://speclab.cr.usgs.gov/spectral.lib06/ds231/ASCII/V/cheatgrass_anp92-11a_veg.29744.asc"))
    s.run()

    self.assertAlmostEqual(s.outputs.apparent_radiance, 29.316, delta=0.002)


  def test_usgs_spectra_from_file(self):
    s = SixS()
    s.ground_reflectance = GroundReflectance.HomogeneousLambertian(Spectra.import_from_usgs("./test/butlerite_gds25.3947.asc"))
    s.run()

    self.assertAlmostEqual(s.outputs.apparent_radiance, 180.818, delta=0.002)



class AltitudesTest(unittest.TestCase):

  def test_custom_sensor_altitude(self):
    s = SixS()
    s.altitudes.set_sensor_custom_altitude(3, 0.26)
    s.run()

    self.assertAlmostEqual(s.outputs.apparent_radiance, 147.964, delta=0.002)

  def test_custom_target_altitude(self):
    s = SixS()
    s.altitudes.set_target_custom_altitude(7)
    s.run()

    self.assertAlmostEqual(s.outputs.apparent_radiance, 139.192, delta=0.002)

  def test_custom_altitudes(self):
    s = SixS()
    s.altitudes.set_target_custom_altitude(7)
    s.altitudes.set_sensor_custom_altitude(50, 0.26)
    s.run()

    self.assertAlmostEqual(s.outputs.apparent_radiance, 158.101, delta=0.002)

  def test_satellite_level(self):
    s = SixS()
    s.altitudes.set_sensor_satellite_level()
    s.run()

    self.assertAlmostEqual(s.outputs.apparent_radiance, 165.188, delta=0.002)

  def test_changing_levels(self):
    s = SixS()
    s.altitudes.set_sensor_custom_altitude(1)
    s.run()

    self.assertAlmostEqual(s.outputs.apparent_radiance, 142.053, delta=0.002)

    s.altitudes.set_sensor_satellite_level()
    s.run()

    self.assertAlmostEqual(s.outputs.apparent_radiance, 165.188, delta=0.002)

  def test_target_pressure(self):
    s = SixS()
    s.altitudes.set_sensor_satellite_level()
    s.altitudes.set_target_pressure(200)
    s.run()

    self.assertAlmostEqual(s.outputs.apparent_radiance, 165.188, delta=0.002)