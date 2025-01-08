#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Script to load aux-files from two-photon, fUSI and behavior setups (.lvd, .eye and .vid)

Created on Tue Jan 28, 2020

@author: pgoltstein
"""

# Imports
import os, glob
import datetime
import numpy as np


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Supporting functions

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

    def __init__(self, filepath=".", filename=None, auxsettingsfile=None, nimagingplanes=1, behavior_only=False, fUSI=False):
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
        self._behavior_only = behavior_only
        self._fUSI = fUSI

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
        if not self._behavior_only and not self._fUSI:
            self._imframes, self._imifi = self._calculate_imaging_frames()
            self._darkfr_on, self._darkfr_off, self._dataonsetframe = self._calculate_darkframes_dataonset()
            self._shutter_open_fr, self._shutter_closed_fr = self._calculate_shutter_onset_offset_fr()
        elif not self._behavior_only and self._fUSI:
            self._imframes, self._imifi = self._calculate_imaging_frames()
            self._darkfr_on, self._darkfr_off, self._dataonsetframe = 0,0,0
            self._shutter_open_fr, self._shutter_closed_fr = self._calculate_shutter_onset_offset_fr()
        else:
            self._imframes, self._imifi = 0, 0.01
            self._darkfr_on, self._darkfr_off, self._dataonsetframe = 0,0,0
            self._shutter_open_fr, self._shutter_closed_fr = 0,0

    # properties
    def __str__(self):
        """ Returns a printable string with summary output """
        if self._behavior_only:
            return "AuxData file {} from {}\n* Channel settings: {}\n  {} channels, {} datapoints, samplingfreq={}Hz, max input={}".format( self._auxfilename, self._datetime, self._auxsettingsfile, self._nchan, self._n, self._sf, self._maxV )
        else:
            return "AuxData file {} from {}\n* Channel settings: {}\n  {} channels, {} datapoints, samplingfreq={}Hz, max input={}V\n  {} imaging frames, imaging samplingfreq={:0.2f}Hz, #planes={}".format( self._auxfilename, self._datetime, self._auxsettingsfile, self._nchan, self._n, self._sf, self._maxV, len(self._imframes), self.imagingsf, self._nimagingplanes )

    @property
    def name(self):
        """ Returns the name of the aux file """
        return self._auxfilename

    @property
    def imagingifi(self):
        """ Returns the real inter frame interval of the imaging stack """
        return self._imifi

    @property
    def imagingsf(self):
        """ Returns the real sampling frequency of the imaging stack """
        return 1/self._imifi

    @property
    def sf(self):
        """ Returns the sampling frequency of the auxdata """
        return self._sf

    @property
    def imagingframes(self):
        """ Returns the onset timestamp of each imaging frame """
        return self._imframes

    @property
    def darkframes(self):
        """ Returns the onset and offset of the darkframes """
        return self._darkfr_on, self._darkfr_off

    @property
    def shuttertimestamps(self):
        """ Returns the onset and offset of the shutter in timestamps (s)"""
        return self._shutter_open_fr/self._sf, self._shutter_closed_fr/self._sf

    @property
    def dataonsetframe(self):
        """ Returns the onset frame of the clean imaging period """
        return self._dataonsetframe

    @property
    def rightreward(self):
        """ calculates the imaging frame for each right reward """
        return self._process_channel_to_frames_or_ts("rightreward", "on")

    @property
    def leftreward(self):
        """ calculates the imaging frame for each left reward """
        return self._process_channel_to_frames_or_ts("leftreward", "on")

    @property
    def rightlicks(self):
        """ calculates the imaging frame for each right lick """
        return self._process_channel_to_frames_or_ts("rightlick", "off")

    @property
    def leftlicks(self):
        """ calculates the imaging frame for each left lick """
        return self._process_channel_to_frames_or_ts("leftlick", "off")

    @property
    def stimulus_onsets(self):
        """ calculates the imaging frames in which the stimulus onset happened """
        return self._process_channel_to_frames_or_ts("stimulusonset", "on")

    @property
    def stimulus_offsets(self):
        """ calculates the imaging frames in which the stimulus onset happened """
        return self._process_channel_to_frames_or_ts("stimulusonset", "off")

    @property
    def responsewindow_onsets(self):
        """ calculates the imaging frames in which the response window onset happened """
        return self._process_channel_to_frames_or_ts("responsewindowonset", "on")

    @property
    def responsewindow_offsets(self):
        """ calculates the imaging frames in which the response window closed (either by timing out, or by a response lick) """
        responsewindow_on = self._process_channel_to_frames_or_ts("responsewindowonset", "on")
        responsewindow_off = self._process_channel_to_frames_or_ts("responsewindowonset", "off")
        timeout_on = self._process_channel_to_frames_or_ts("timeoutonset", "on")
        for tr_nr,(rw_on,rw_off) in enumerate(zip(responsewindow_on,responsewindow_off)):
            timeout_in_resp_win = np.logical_and(timeout_on>=rw_on, timeout_on<=rw_off)
            if np.nansum( timeout_in_resp_win ) > 0:
                responsewindow_off[tr_nr] = timeout_on[timeout_in_resp_win]
        return responsewindow_off

    @property
    def waitfornolick_onsets(self):
        """ calculates the imaging frames in which the waitfornolick window onset happened """
        return self._process_channel_to_frames_or_ts("waitfornolick", "on")

    @property
    def waitfornolick_offsets(self):
        """ returns the imaging frames in which the waitfornolick window closed (stimulus onset) """
        return self.stimulus_onsets

    @property
    def timeout_onsets(self):
        """ calculates the imaging frames in which the timeout started """
        return self._process_channel_to_frames_or_ts("timeoutonset", "on")

    @property
    def timeout_offsets(self):
        """ calculates the imaging frames in which the timeout ended """
        return self._process_channel_to_frames_or_ts("timeoutonset", "off")

    @property
    def rawposition(self):
        """ Returns the raw position data of the ball
        """
        # Get channel info
        channelnr = self._channelsettings["ball"]["nr"]

        # Get the position data and derivative
        return self._auxdata[:,channelnr]

    @property
    def position(self):
        """ Returns the cleaned up position data of the ball
        """
        # Get channel info
        channelnr = self._channelsettings["ball"]["nr"]

        # Get the position data and derivative
        position = np.array(self._auxdata[:,channelnr])
        posdiff = np.diff(position)

        # Find and remove the up and down flips
        flips = np.argwhere(np.abs(posdiff)>2).ravel()
        for f in flips:
            lastposdiff = position[f]-position[f+1]
            position[(f+1):] = position[(f+1):] + lastposdiff

        # Return data
        return position

    @property
    def runningspeed(self):
        """ calculates the running speed of the animal (per imaging frame or into 100 ms bins for behavior only)
        """
        # Get the derivative of the position data
        speed = np.diff(self.position)

        # smooth by 100 ms
        speed = smooth(speed, int(self._sf/10))

        # Multiply by sampling freq to result in V/s
        speed = speed * self._sf

        # Convert to frames or bins
        if self._behavior_only:
            n_sampl_bin = int(self._sf/100) # number of samples per 100 ms
            n_bins = np.floor(len(speed) / n_sampl_bin).astype(int)
            binned_speed = np.zeros((n_bins,))
            for b in range(n_bins):
                start_samp = (b*n_sampl_bin)
                stop_samp = ((b+1)*n_sampl_bin)
                binned_speed[b] = np.mean(speed[start_samp:stop_samp])
            return binned_speed
        else:
            frameonsets_speed = np.zeros_like( self._imframes ).astype(float)
            frame_gap_aux = np.floor( np.mean( self._imframes[1:] - self._imframes[:-1] ) ).astype(int)
            for ix in range(len(self._imframes)):
                frameonsets_speed[ix] = np.mean( speed[int(self._imframes[ix]):int(self._imframes[ix]+frame_gap_aux)] )
            return frameonsets_speed.ravel()


    @property
    def imagingplane(self):
        """ Returns the currently selected image plane (relevant for exact frame timing) """
        return self._imagingplane

    @imagingplane.setter
    def imagingplane(self,imagingplane_nr):
        """ Sets the imaging plane (relevant for exact frame timing) """
        self._imagingplane = int(imagingplane_nr)

    # Methods
    def raw_channel(self,nr=0,name=None):
        """ returns the raw channel data, by channel number or name """
        if name is not None:
            nr = self._channelsettings[name]["nr"]
        return self._auxdata[:,nr]

    def channel(self,nr=0,name=None):
        """ returns the raw channel data, by channel number or name """
        if name is not None:
            nr = self._channelsettings[name]["nr"]
        if self._behavior_only:
            return self._auxdata[:,nr]
        else:
            return self._auxdata[self.imagingframes[0,0]:,nr]

    def _process_channel_to_frames_or_ts(self, eventname, onoff="on"):
        """ calculates the imaging frame or timestamp (10 ms unit) for each event """

        # Get channel info
        event_channelname = self._processingsettings[eventname]["channel"]
        event_channelnr = self._channelsettings[event_channelname]["nr"]
        channelthreshold = self._processingsettings[eventname]["threshold"]

        # Threshold the channel
        channeldata = self._auxdata[:,event_channelnr]
        if onoff == "on":
            channeldata = np.diff((channeldata > channelthreshold) * 1.0) > 0
        elif onoff == "off":
            channeldata = np.diff((channeldata > channelthreshold) * 1.0) < 0

        # Find the event onsets
        event_aux = np.argwhere(channeldata) + 1 # +1 compensates shift introduced by np.diff

        # Convert aux indices to milliseconds / frames
        if self._behavior_only:
            event_times = np.zeros((len(event_aux),))
            for ix in range(len(event_aux)):
                event_times[ix] = 100 * (event_aux[ix]/self._sf)

            # Return event times
            return event_times.ravel()
        else:
            event_fr = np.zeros_like(event_aux)
            for ix in range(len(event_aux)):
                event_fr[ix] = np.argmin( np.abs(self._imframes - event_aux[ix]) )

            # Return event frames
            return event_fr.astype(int).ravel()

    # Internal methods
    def _calculate_shutter_onset_offset_fr(self):
        """ Calculates the onset and offset of the two photon shutter """
        # Get channel info
        shutterchannelname = self._processingsettings["shutter"]["channel"]
        shutterchannelnr = self._channelsettings[shutterchannelname]["nr"]
        channelthreshold = self._processingsettings["shutter"]["threshold"]

        # Threshold the frames
        channeldata = self._auxdata[:,shutterchannelnr]

        # Find onset and offset in aux channel
        shutter_onset = np.argwhere( np.diff((channeldata > channelthreshold) * 1.0) > 0 ) + 1 # +1 compensates shift introduced by np.diff
        shutter_offset = np.argwhere( np.diff((channeldata > channelthreshold) * 1.0) < 0 ) + 1 # +1 compensates shift introduced by np.diff

        if len(shutter_onset) > 1:
            shutter_onset = shutter_onset.ravel()[0]
            print("  !! Multiple shutter onsets found, taking first one: {} !!".format(shutter_onset))

        if len(shutter_offset) > 1:
            shutter_offset = shutter_offset.ravel()[0]
            print("  !! Multiple shutter offsets found, taking first one: {} !!".format(shutter_offset))

        return int(shutter_onset), int(shutter_offset)

    def _calculate_darkframes_dataonset(self):
        """ Calculates the onset and offset of the darkframes and the data onset frame """
        # Get channel info
        darkframeschannelname = self._processingsettings["darkframes"]["channel"]
        channelthreshold = self._processingsettings["darkframes"]["threshold"]
        channelresolution = self._processingsettings["darkframes"]["resolution"]
        channelvalue = self._processingsettings["darkframes"]["value"]

        # Get clean channel signal
        try:
            cleaned_channel = self._clean_channel( darkframeschannelname, channelthreshold, channelresolution )
        except:
            cleaned_channel = self._clean_channel( darkframeschannelname, channelthreshold, channelresolution, set_first_to_zero=True )

        # Find onset in aux channel
        df_onset = np.argwhere( np.diff((cleaned_channel==channelvalue) * 1.0) > 0 ) + 1 # +1 compensates shift introduced by np.diff
        df_offset = np.argwhere( np.diff((cleaned_channel!=channelvalue) * 1.0) > 0 ) + 1 # +1 compensates shift introduced by np.diff

        # Convert to frames
        if df_onset.size == 0 and df_offset.size == 0:
            df_onset_fr = None
            df_offset_fr = None
            dataonset = 0
            return df_onset_fr, df_offset_fr, dataonset
        else:
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
        if not self._fUSI:
            channeldata = np.diff((channeldata > channelthreshold) * 1.0) > 0
        else:
            channeldata = np.abs(np.diff((channeldata > channelthreshold) * 1.0)) > 0

        # Find the frame onsets
        frameonsets = np.argwhere(channeldata) + 1 # +1 compensates shift introduced by np.diff

        # In some conditions, the fUSI setup has more early triggers, in that case, remove those
        if self._fUSI:
            
            # Get the inter frame intervals
            ifis = frameonsets[1:]-frameonsets[:-1]

            # Get the mean ifi from the middle section (so ignoring possible artifacty triggers at start or end)
            mean_ifi = np.mean(ifis[20:-20])

            # Iteratively remove initial frame onsets with too short ifi's
            for i in range(100):
                if ifis[i] < 0.7*mean_ifi:
                    frameonsets = frameonsets[1:]
                else:
                    break
            
            # Remove first and last detected frame for fUSI (are not actual frames)
            # The fUSI setup starts with the trigger to go "on", then at frame 0 it turns "off", and then the next frame "on", etc.
            frameonsets = frameonsets[1:-1]

        # Adjust for multilevel (fast piezo) stacks
        if self._nimagingplanes > 1:
            frameonsets = frameonsets[self.imagingplane::self._nimagingplanes]

        # Get inter frame interval and return data
        ifi_samples = np.round(np.mean(frameonsets[1:]-frameonsets[:-1]))
        ifi = ifi_samples / self._sf
        return frameonsets, ifi

    def _clean_channel(self, channelname, threshold, resolution, set_first_to_zero=False):
        """ cleans up the random electrical noise in channel """
        # Get channel data
        channelnr = self._channelsettings[channelname]["nr"]
        channeldata = self._auxdata[:,channelnr]
        if set_first_to_zero:
            print("Warning, changing first data point to zero in aux channel to help detect the first onset")
            channeldata[0] = 0.0

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
