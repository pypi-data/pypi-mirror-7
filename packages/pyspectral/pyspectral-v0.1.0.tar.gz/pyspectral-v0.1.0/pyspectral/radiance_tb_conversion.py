#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <a000680@c14526.ad.smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Conversion between radiances and brightness temperatures for the IR bands of
various satellite sensors
"""

import logging
LOG = logging.getLogger(__name__)

import numpy as np
from pyspectral.blackbody import blackbody, blackbody_wn

WAVE_LENGTH = 'wavelength'
WAVE_NUMBER = 'wavenumber'

EPSILON = 0.01
TB_MIN = 150.
TB_MAX = 360.

# Meteosat SEVIRI regression parameters according to documentation
# (PDF_EFFECT_RAD_TO_BRIGHTNESS.pdf).
#
# Tb = C2 * νc/{α * log[C1*νc**3 / L + 1]} - β/α
#
# L = C1 * νc**3 / (exp (C2 νc / [αTb + β]) − 1)
#
# C1 = 2 * h * c**2 and C2 = hc/k
#
# Units are cm-1 for the channel/band central wavenumber, K for the beta
# parameter, and the alpha parameter is dimensionless:
#
SEVIRI = {'IR3.9': {'8': [2567.330, 0.9956, 3.410],
                    '9': [2568.832, 0.9954, 3.438],
                    '10': [],
                    },
          'WV6.2': {'8': [1598.103, 0.9962, 2.218],
                    '9': [1600.548, 0.9963, 2.185],
                    },
          'WV7.3': {'8': [1362.081, 0.9991, 0.478],
                    '9': [1360.330, 0.9991, 0.470],
                    },
          'IR8.7': {'8': [1149.069, 0.9996, 0.179],
                    '9': [1148.620, 0.9996, 0.179],
                    },
          'IR9.7': {'8': [1034.343, 0.9999, 0.060],
                    '9': [1035.289, 0.9999, 0.056],
                    },
          'IR10.8': {'8': [930.647, 0.9983, 0.625],
                     '9': [931.700, 0.9983, 0.640],
                     },
          'IR12.0': {'8': [839.660, 0.9988, 0.397],
                     '9': [836.445, 0.9988, 0.408],
                     },
          'IR13.4': {'8': [752.387, 0.9981, 0.578],
                     '9': [751.792, 0.9981, 0.561],
                     },
          }


class RadTbConverter(object):

    """A radiance to brightness temperature calculator

    It can do the conversion either based on direct use of the band relative
    spectral response function, or on officially (by satellite agencies)
    tabulated standard values using non-linear regression methods.
    Methods:
      1: Spectral response function
      2: non-linear approximation using tabulated coefficients 
    """

    def __init__(self, platform, satnum, instrument, bandname, method=1,
                 **options):
        """E.g.:
           platform = 'meteosat'
           satnum = '9'
           instrument = 'seviri'
        """
        self.platform = platform
        self.satnumber = satnum
        self.instrument = instrument
        self.rsr = None
        self.bandname = bandname

        if 'detector' in options:
            self.detector = options['detector']
        else:
            self.detector = 'det-1'

        if 'wavespace' in options:
            if options['wavespace'] not in [WAVE_LENGTH, WAVE_NUMBER]:
                raise AttributeError('Wave space not %s or %s!' % (WAVE_LENGTH,
                                                                   WAVE_NUMBER))
            self.wavespace = options['wavespace']
        else:
            self.wavespace = WAVE_LENGTH

        self._wave_unit = ''
        self._wave_si_scale = 1.0

        if 'tb_resolution' in options:
            self.tb_resolution = options['tb_resolution']
        else:
            self.tb_resolution = 0.1
        self.tb_scale = 1. / self.tb_resolution

        if method == 1:
            self.get_rsr()

    def get_rsr(self):
        """Get all spectral responses for the sensor"""

        from pyspectral.utils import convert2wavenumber
        from pyspectral.rsr_reader import RelativeSpectralResponse

        sensor = RelativeSpectralResponse(self.platform, self.satnumber,
                                          self.instrument)
        LOG.debug("Wavenumber? " + str(self.wavespace))
        if self.wavespace == WAVE_NUMBER:
            LOG.debug("Converting to wavenumber...")
            self.rsr, info = convert2wavenumber(sensor.rsr)
        else:
            self.rsr = sensor.rsr
            info = {'unit': sensor.unit, 'si_scale': sensor.si_scale}

        self._wave_unit = info['unit']
        self._wave_si_scale = info['si_scale']

    def _getsatname(self):
        """Get the satellite name used in the rsr-reader, from the platform and
        number"""

        if self.platform == "meteosat":
            return 'met%d' % int(self.satnumber)
        else:
            raise NotImplementedError('Platform ' + str(self.platform) +
                                      ' not yet supported...')

    def tb2radiance(self, tb_, bandname, lut=False):
        """Get the radiance from the brightness temperature (Tb) given the
        band name. 
        """
        from scipy import integrate

        if not bandname and not np.any(lut):
            raise SyntaxError('Either a band name or a lut needs ' +
                              'to be provided as input to the function call!')

        if lut:
            ntb = (tb_ * self.tb_scale).astype('int16')
            start = int(lut['tb'][0] * self.tb_scale)
            return lut['radiance'][ntb - start]

        if self.wavespace == WAVE_LENGTH:
            wv_ = (self.rsr[bandname][self.detector]['wavelength'] *
                   self._wave_si_scale)
            resp = self.rsr[bandname][self.detector]['response']
            planck = blackbody(wv_, tb_) * resp
        elif self.wavespace == WAVE_NUMBER:
            wv_ = (self.rsr[bandname][self.detector]['wavenumber'] *
                   self._wave_si_scale)
            resp = self.rsr[bandname][self.detector]['response']
            planck = blackbody_wn(wv_, tb_) * resp
        else:
            raise NotImplementedError(str(self.wavespace) +
                                      ' representation of ' +
                                      'rsr data not supported!')

        radiance = integrate.trapz(planck, wv_) / np.trapz(resp, wv_)
        if self.wavespace == WAVE_NUMBER:
            unit = 'W/m^2 sr^-1 (m^-1)^-1'
            scale = 1.0
        else:
            unit = 'W/m^2 sr^-1 m^-1'
            scale = 1.0

        return {'radiance': radiance,
                'unit': unit,
                'scale': scale}

    def make_tb2rad_lut(self, bandname, filepath):
        """Generate a Tb to radiance look-up table"""

        tb_ = np.arange(TB_MIN, TB_MAX, self.tb_resolution)
        retv = self.tb2radiance(tb_, bandname)
        rad = retv['radiance']
        np.savez(filepath, tb=tb_, radiance=rad.compressed())

    def read_tb2rad_lut(self, filepath):
        """Read the Tb to radiance look-up table"""

        retv = np.load(filepath, 'r')
        return retv

    def tb2radiance_simple(self, tb_, bandname):
        """Get the radiance from the Tb using the simple non-linear regression
        method. SI units of course!"""

        # L = C1 * νc**3 / (exp (C2 νc / [αTb + β]) − 1)
        #
        # C1 = 2 * h * c**2 and C2 = hc/k
        #
        from pyspectral.blackbody import (H_PLANCK, K_BOLTZMANN, C_SPEED)

        c_1 = 2 * H_PLANCK * C_SPEED ** 2
        c_2 = H_PLANCK * C_SPEED / K_BOLTZMANN

        vc_ = SEVIRI[bandname][self.satnumber][0]
        # Multiply by 100 to get SI units!
        vc_ *= 100.0
        alpha = SEVIRI[bandname][self.satnumber][1]
        beta = SEVIRI[bandname][self.satnumber][2]

        radiance = c_1 * vc_ ** 3 / \
            (np.exp(c_2 * vc_ / (alpha * tb_ + beta)) - 1)

        unit = 'W/m^2 sr^-1 (m^-1)^-1'
        scale = 1.0
        #unit = 'mW/m^2 sr^-1 (cm^-1)^-1'
        #scale = 10.0
        return {'radiance': radiance,
                'unit': unit,
                'scale': scale}

    def radiance2tb_simple(self, rad, bandname):
        """Get the Tb from the radiance using the simple non-linear regression
        method. 
        rad: Radiance in units = 'mW/m^2 sr^-1 (cm^-1)^-1'
        """
        #
        # Tb = C2 * νc/{α * log[C1*νc**3 / L + 1]} - β/α
        #
        # C1 = 2 * h * c**2 and C2 = hc/k
        #
        from pyspectral.blackbody import (H_PLANCK, K_BOLTZMANN, C_SPEED)

        c_1 = 2 * H_PLANCK * C_SPEED ** 2
        c_2 = H_PLANCK * C_SPEED / K_BOLTZMANN

        vc_ = SEVIRI[bandname][self.satnumber][0]
        # Multiply by 100 to get SI units!
        vc_ *= 100.0
        alpha = SEVIRI[bandname][self.satnumber][1]
        beta = SEVIRI[bandname][self.satnumber][2]

        tb_ = c_2 * vc_ / \
            (alpha * np.log(c_1 * vc_ ** 3 / rad + 1)) - beta / alpha

        return tb_
