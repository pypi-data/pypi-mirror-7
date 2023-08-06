#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, 2014 Adam.Dybbroe

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

"""Interface to VIIRS relative spectral responses
"""

import logging
LOG = logging.getLogger(__name__)

import ConfigParser
import os

try:
    CONFIG_FILE = os.environ['PSP_CONFIG_FILE']
except KeyError:
    LOG.exception('Environment variable PSP_CONFIG_FILE not set!')
    raise

if not os.path.exists(CONFIG_FILE) or not os.path.isfile(CONFIG_FILE):
    raise IOError(str(CONFIG_FILE) + " pointed to by the environment " +
                  "variable PSP_CONFIG_FILE is not a file or does not exist!")

import numpy as np
from pyspectral.utils import get_central_wave

VIIRS_BAND_NAMES = ['M1', 'M2', 'M3', 'M4', 'M5',
                    'M6', 'M7', 'M8', 'M9', 'M10',
                    'M11', 'M12', 'M13', 'M14', 'M15', 'M16',
                    'I1', 'I2', 'I3', 'I4', 'I5',
                    'DNB']

#: Default time format
_DEFAULT_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

#: Default log format
_DEFAULT_LOG_FORMAT = '[%(levelname)s: %(asctime)s : %(name)s] %(message)s'


class ViirsRSR(object):

    """Container for the (S-NPP) VIIRS RSR data"""

    def __init__(self, bandname, satname='npp'):
        """
        """
        self.satname = satname
        self.bandname = bandname
        self.filename = None
        self.rsr = None

        conf = ConfigParser.ConfigParser()
        try:
            conf.read(CONFIG_FILE)
        except ConfigParser.NoSectionError:
            LOG.exception('Failed reading configuration file: ' +
                          str(CONFIG_FILE))
            raise

        options = {}
        for option, value in conf.items('viirs', raw=True):
            options[option] = value

        for option, value in conf.items('general', raw=True):
            options[option] = value

        self.output_dir = options.get('rsr_dir', './')

        self._get_bandfile(**options)
        LOG.debug("Filename: " + str(self.filename))
        self._load()

    def _get_bandfile(self, **options):
        """Get the VIIRS rsr filename"""

        band_file = None

        # Need to understand why there are A&B files for band M16. FIXME!
        # Anyway, the absolute response differences are small, below 0.05
        if self.bandname == 'M16':
            values = {"bandname": 'M16A'}
        else:
            values = {"bandname": self.bandname}

        paths = [options["iband_visnir_path"],
                 options["iband_ir_path"],
                 options["mband_visnir_path"],
                 options["mband_ir_path"],
                 options["dnb_path"]
                 ]
        fnames = [options["iband_visnir_names"] % values,
                  options["iband_ir_names"] % values,
                  options["mband_visnir_names"] % values,
                  options["mband_ir_names"] % values,
                  options["dnb_name"] % values
                  ]

        LOG.debug("paths = " + str(paths))
        LOG.debug("fnames = " + str(fnames))

        for path, fname in zip(paths, fnames):
            band_file = os.path.join(path, fname)
            if os.path.exists(band_file):
                self.filename = band_file
                return

        if not band_file:
            raise IOError("Couldn't find an existing file for this band: " +
                          str(self.bandname))

    def _load(self, scale=0.001):
        """Load the VIIRS RSR data for the band requested
        """
        import numpy as np

        try:
            data = np.genfromtxt(self.filename,
                                 unpack=True, skip_header=1,
                                 names=['bandname',
                                        'detector',
                                        'subsample',
                                        'wavelength',
                                        'band_avg_snr',
                                        'asr',
                                        'response',
                                        'quality_flag',
                                        'xtalk_flag'],
                                 dtype=[('bandname', '|S3'),
                                        ('detector', '<i4'),
                                        ('subsample', '<i4'),
                                        ('wavelength', '<f8'),
                                        ('band_avg_snr', '<f8'),
                                        ('asr', '<f8'),
                                        ('response', '<f8'),
                                        ('quality_flag', '<i4'),
                                        ('xtalk_flag', '<i4')])
        except ValueError:
            data = np.genfromtxt(self.filename,
                                 unpack=True, skip_header=1,
                                 names=['bandname',
                                        'detector',
                                        'subsample',
                                        'wavelength',
                                        'response'],
                                 dtype=[('bandname', '|S3'),
                                        ('detector', '<i4'),
                                        ('subsample', '<i4'),
                                        ('wavelength', '<f8'),
                                        ('response', '<f8')])
        wavelength = data['wavelength'] * scale
        response = data['response']
        det = data['detector']

        detectors = {}
        for idx in range(int(max(det))):
            detectors["det-%d" % (idx + 1)] = {}
            detectors[
                "det-%d" % (idx + 1)]['wavelength'] = np.repeat(wavelength, np.equal(det, idx + 1))
            detectors[
                "det-%d" % (idx + 1)]['response'] = np.repeat(response, np.equal(det, idx + 1))

        self.rsr = detectors


if __name__ == "__main__":

    import sys
    LOG = logging.getLogger('viirs_rsr')
    handler = logging.StreamHandler(sys.stderr)

    formatter = logging.Formatter(fmt=_DEFAULT_LOG_FORMAT,
                                  datefmt=_DEFAULT_TIME_FORMAT)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    LOG.setLevel(logging.DEBUG)
    LOG.addHandler(handler)

    import h5py

    platform_id = "npp"
    viirs = ViirsRSR('M1', 'npp')
    filename = os.path.join(viirs.output_dir,
                            "rsr_viirs_%s.h5" % platform_id)

    with h5py.File(filename, "w") as h5f:
        h5f.attrs['description'] = 'Relative Spectral Responses for VIIRS'
        h5f.attrs['platform'] = platform_id
        h5f.attrs['sat_number'] = np.nan
        h5f.attrs['band_names'] = VIIRS_BAND_NAMES

        for chname in VIIRS_BAND_NAMES:
            viirs = ViirsRSR(chname)
            grp = h5f.create_group(chname)
            grp.attrs['number_of_detectors'] = len(viirs.rsr.keys())
            # Loop over each detector to check if the sampling wavelengths are
            # identical:
            det_names = viirs.rsr.keys()
            wvl = viirs.rsr[det_names[0]]['wavelength']
            wvl_is_constant = True
            for det in det_names[1:]:
                if not np.alltrue(wvl == viirs.rsr[det_names[0]]['wavelength']):
                    wvl_is_constant = False

            if wvl_is_constant:
                arr = viirs.rsr[det_names[0]]['wavelength']
                dset = grp.create_dataset('wavelength', arr.shape, dtype='f')
                dset.attrs['unit'] = 'm'
                dset.attrs['scale'] = 1e-06
                dset[...] = arr

            # Loop over each detector:
            for det in viirs.rsr:
                det_grp = grp.create_group(det)
                wvl = viirs.rsr[det]['wavelength'][
                    ~np.isnan(viirs.rsr[det]['wavelength'])]
                rsp = viirs.rsr[det]['response'][
                    ~np.isnan(viirs.rsr[det]['wavelength'])]
                det_grp.attrs[
                    'central_wavelength'] = get_central_wave(wvl, rsp)
                if not wvl_is_constant:
                    arr = viirs.rsr[det]['wavelength']
                    dset = det_grp.create_dataset(
                        'wavelength', arr.shape, dtype='f')
                    dset.attrs['unit'] = 'm'
                    dset.attrs['scale'] = 1e-06
                    dset[...] = arr

                arr = viirs.rsr[det]['response']
                dset = det_grp.create_dataset('response', arr.shape, dtype='f')
                dset[...] = arr
