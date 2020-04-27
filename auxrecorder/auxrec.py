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

    def __init__(self, filepath=".", filename=None, auxsettingsfile=None):
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
            self_path = os.path.dirname(os.path.realpath(__file__))
            settings_path = os.path.join( self_path.split(os.path.sep)[:-1].join(os.path.sep), "settings" )
            auxsettingsfile = os.path.join( settings_path, "default.auxsettings.py" )
        settings = {}
        with open(auxsettingsfile) as f:
            exec(f.read(), settings)
            self._channelsettings = settings["auxchannels"]
        self._auxsettingsfile = auxsettingsfile

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

        # Process aux channels
        self._imframes, self._imifi = self._calculate_imaging_frames()


    # properties
    def __str__(self):
        """ Returns a printable string with summary output """
        return "AuxData file {} from {}\n* Channel settings: {}\n* {} channels, {} datapoints, samplingfreq={}Hz, max input={}V".format( self._auxfilename, self._datetime, self._auxsettingsfile, self._nchan, self._n, self._sf, self._maxV )

    @property
    def imagingifi(self):
        """ Returns the real inter frame interval of the imaging stack """
        return self._imifi

    @property
    def imagingsf(self):
        """ Returns the real sampling frequency of the imaging stack """
        return 1/self._imifi

    # Methods
    def raw_channel(self,nr=0):
        """ returns the raw channel data, by channel number """
        return self._auxdata[:,nr]

    # Internal methods
    def _calculate_imaging_frames(self):
        """ calculates the aux samples that correspond with the imaging frame onsets """
        # Get channel info
        framechannelnr = self._channelsettings["frame"]["nr"]
        channelmin = self._channelsettings["frame"]["range"][0]
        channelmax = self._channelsettings["frame"]["range"][1]

        # Threshold the frames at the middle value
        channeldata = self._auxdata[:,3]
        channeldata = (channeldata-channelmin) / (channelmax-channelmin)

        # Find and return the frame onsets
        channeldata = np.diff((channeldata > 0.5) * 1.0) > 0
        frameonsets = np.argwhere(channeldata)
        ifi_samples = np.round(np.mean(frameonsets[1:]-frameonsets[:-1]))
        ifi = ifi_samples / self._sf
        return frameonsets, ifi

    def _process_channel(self,channelname):
        """ cleans up the random electrical noise in the channels """

        channelnr = self._channelsettings[channelname]["nr"]
        print("channelnr = {}".format(channelnr))
        channelmin = self._channelsettings[channelname]["range"][0]
        print("channelmin = {}".format(channelmin))
        channelmax = self._channelsettings[channelname]["range"][1]
        print("channelmax = {}".format(channelmax))
        channelnval = self._channelsettings[channelname]["nvalues"]
        print("channelnval = {}".format(channelnval))

        channeldata = self._auxdata[:,channelnr]
        channeldata = (channeldata-channelmin) / (channelmax-channelmin)
        channeldata = np.round(channeldata * (channelnval-1))

        return channeldata
