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
from scipy import stats as scistats

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

    def __init__(self, filepath=".", filename=None, auxsettingsfile=None, nimagingplanes=1):
        """ Initializes the class and loads and processes all auxdata
            Inputs:
            - filepath: Path to where the .lvd file is located
            - filename: Optional exact filename
            - auxsettingsfile: Optional filename holding the auxdata metadata such as the channel specifications (otherwise loaded from the file "default.auxsettings.py")
            - nimagingplanes: Number of multilevel planes of imaging stack
        """
        super(LvdAuxRecorder, self).__init__()

        # Get filename and store inputs
        if filename is None: filename = "*.lvd"
        self._auxfile = glob.glob( os.path.join(filepath,filename) )[0]
        self._auxfilename = self._auxfile.split(os.path.sep)[-1]
        self._nimagingplanes = nimagingplanes
        self._imagingplane = 0

        # Get settings
        if auxsettingsfile is None:
            self_path = os.path.dirname(os.path.realpath(__file__))
            settings_path = os.path.join( os.path.sep.join(  self_path.split(os.path.sep)[:-1] ), "settings" )
            auxsettingsfile = os.path.join( settings_path, "default.auxsettings.py" )
        settings = {}
        with open(auxsettingsfile) as f:
            exec(f.read(), settings)
            self._channelsettings = settings["auxchannels"]
            self._processingsettings = settings["auxprocessing"]
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
        self._darkfr_on, self._darkfr_off, self._dataonsetframe = self._calculate_darkframes_dataonset()


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

    @property
    def darkframes(self):
        """ Returns the onset and offset of the darkframes """
        return self._darkfr_on, self._darkfr_off

    @property
    def dataonsetframe(self):
        """ Returns the onset frame of the clean imaging period """
        return self._dataonsetframe

    @property
    def imagingplane(self):
        """ Returns the currently selected image plane (relevant for exact frame timing) """
        return self._imagingplane

    @imagingplane.setter
    def imagingplane(self,imagingplane_nr):
        """ Sets the imaging plane (relevant for exact frame timing) """
        self._imagingplane = int(imagingplane_nr)

    # Methods
    def raw_channel(self,nr=0):
        """ returns the raw channel data, by channel number """
        return self._auxdata[:,nr]

    # Internal methods
    def _calculate_darkframes_dataonset(self):
        """ Calculates the onset and offset of the darkframes and the data onset frame """
        # Get channel info
        darkframeschannelname = self._processingsettings["darkframes"]["channel"]
        channelthreshold = self._processingsettings["darkframes"]["threshold"]
        channelresolution = self._processingsettings["darkframes"]["resolution"]
        channelvalue = self._processingsettings["darkframes"]["value"]

        # Get clean channel signal
        cleaned_channel = self._clean_channel( darkframeschannelname, channelthreshold, channelresolution )

        # Find onset in aux channel
        df_onset = np.argwhere( np.diff((cleaned_channel==channelvalue) * 1.0) > 0 ) + 1 # +1 compensates shift introduced by np.diff
        df_offset = np.argwhere( np.diff((cleaned_channel!=channelvalue) * 1.0) > 0 ) + 1 # +1 compensates shift introduced by np.diff

        # Convert to frames
        df_onset_fr = np.argmin( np.abs(self._imframes - df_onset[0]) )
        df_offset_fr = np.argmin( np.abs(self._imframes - df_offset[0]) )
        dataonset = np.ceil( df_offset_fr + self.imagingsf )

        # Return dark frame onset, offset, dataonset; add/subtract 1 for safety
        return int(df_onset_fr+1), int(df_offset_fr-1), int(dataonset+1)

    def _calculate_imaging_frames(self):
        """ calculates the aux samples that correspond with the imaging frame onsets """
        # Get channel info
        framecountchannelname = self._processingsettings["framecounts"]["channel"]
        framecountchannelnr = self._channelsettings[framecountchannelname]["nr"]
        channelthreshold = self._processingsettings["framecounts"]["threshold"]

        # Threshold the frames
        channeldata = self._auxdata[:,framecountchannelnr]
        channeldata = np.diff((channeldata > channelthreshold) * 1.0) > 0

        # Find the frame onsets
        frameonsets = np.argwhere(channeldata) + 1 # +1 compensates shift introduced by np.diff

        # Adjust for multilevel (fast piezo) stacks
        if self._nimagingplanes > 1:
            frameonsets = frameonsets[self.imagingplane::self._nimagingplanes]

        # Get inter frame interval and return data
        ifi_samples = np.round(np.mean(frameonsets[1:]-frameonsets[:-1]))
        ifi = ifi_samples / self._sf
        return frameonsets, ifi

    def _clean_channel(self, channelname, threshold, resolution):
        """ cleans up the random electrical noise in channel """
        # Get channel data
        channelnr = self._channelsettings[channelname]["nr"]
        channeldata = self._auxdata[:,channelnr]

        # Threshold the channel, find 'events'
        channel_up = np.argwhere(np.diff((channeldata > threshold) * 1.0) > 0)
        channel_down = np.argwhere(np.diff((channeldata < threshold) * 1.0) > 0)
        channel_up += 1 # Because of the np.diff above, the frames shifted by 1
        channel_down += 1

        # Loop over events, set to channel value
        cleaneddata = np.zeros_like(channeldata)
        for on,off in zip(channel_up.ravel(),channel_down.ravel()):
            cleanedvalues =  np.round( channeldata[on:off] / resolution )
            values,counts = np.unique(cleanedvalues, return_counts=True)
            cleaneddata[on:off] = values[np.argmax(counts)] * resolution

        # Return cleaned channel
        return cleaneddata
