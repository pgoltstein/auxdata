#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Script to load aux-files from two-photon setups (.lvd, .eye and .vid)

Created on Tue Jan 28, 2020

@author: pgoltstein
"""

# Imports
import os, glob
import datetime
import numpy as np


#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# Functions

def get_channels(auxdata, channels):
    """ Processes aux data into -per imaging frame- values """
    channel_data = {}
    for ch,nr in channels.items():
        channel_data[ch] = auxdata[:,nr]
    return channel_data

def process_channels(auxdata, setup, nstimuli=None, darkframevalue=0.5, stimvalues=(1,5)):
    """ Processes aux data into -per imaging frame- values """
    pass


#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# Classes

class LvdAuxRecorder(object):
    """ Loads and represents .lvd aux data. Auxdata is loaded and recoded to per-frame-values.

        Inputs:

        Aux data can be queried using class properties, e.g:
        * auxtime = aux.timestamp
        * shutter = aux.shutter
        * stimulus = aux.stimulus
        * position = aux.position
        * auxdata = aux.data (2d array with all aux data)

        In addition, the class provides access to the meta data as properties. For instance:
        * samplingfreq = aux.sf returns the sampling frequency of the auxdata
        * nchannels = aux.nchannels returns number of aux channels

    """

    def __init__(self, filepath, filename=None, auxsettingsfile=None):
        """ Initializes the class and loads and processes all auxdata
            Inputs:
            - filepath: Path to where the .lvd file is located
            - filename: Optional exact filename
            - auxsettingsfile: Optional filename holding the auxdata metadata such as the channel specifications (otherwise loaded from the file "default.auxsettings.py")
        """
        super(LvdAuxRecorder, self).__init__()

        # Get filename
        if filename is None: filename = "*.lvd"
        self._auxfile = glob.glob( os.path.join(filepath,filename) )[0]
        self._auxfilename = self._auxfile.split(os.path.sep)[-1]

        # Get settings
        if auxsettingsfile is None:
            auxsettingsfile = os.path.join(os.getcwd(),"default.auxsettings.py")
        settings = {}
        with open(auxsettingsfile) as f:
            exec(f.read(), settings)
            self._channelsettings = settings["auxchannels"]

        # Open the aux file for reading
        with open(self._auxfile, 'rb') as f:

            # Reset file index
            f.seek(0)

            # Get meta data
            self._sf = int(np.fromfile(f, dtype='>f8', count=1))
            self._nchan = int(np.fromfile(f, dtype='>f8', count=1))
            tm = str(int(np.fromfile(f, dtype='>f8', count=1)))
            self._datetime = datetime.datetime(year=int(tm[0:4]), month=int(tm[4:6]), day=int(tm[6:8]), hour=int(tm[8:10]), minute=int(tm[10:12]), second=int(tm[12:14]))
            self._maxV = float(np.fromfile(f, dtype='>f8', count=1))

            # Read aux data
            auxdata = np.fromfile(f, dtype='>f8')
            self._n = int(auxdata.shape[0]/self._nchan)
            self._auxdata = np.reshape(auxdata,(self._n,self._nchan))

        print("AuxData file {} from {}".format( self._auxfilename,self._datetime) )
        print("* Channel settings: {}".format(auxsettingsfile))
        print("* {} channels, {} datapoints, samplingfreq={}, max input = {} V".format( self._nchan, self._n, self._sf, self._maxV ))

    # Shutter
    def _process_shutter(self):
        pass
