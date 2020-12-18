#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Script to load stimulus-files from two-photon setups, from matlab based scripts

Created on Thu May 7, 2020

@author: pgoltstein
"""

# Imports
import os, glob
import datetime
import numpy as np
from scipy.io import loadmat


#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# Classes

class StimulusData(object):
    """ Loads and represents .mat stimulus data.
    """

    def __init__(self, filepath=".", filename=None):
        """ - filepath: Path to where the .mat file is located
            - filename: Optional exact filename
        """

        # Find and load stimulus file
        super(StimulusData, self).__init__()

        # Get filename and store inputs
        if filename is None: filename = "*StimSettings.mat"
        self._stimfile = glob.glob( os.path.join(filepath,filename) )[0]
        self._stimfilename = self._stimfile.split(os.path.sep)[-1]

        # Get date and time of the stimfile
        namesplitted = self._stimfilename.split("-")
        date_split = namesplitted[-3]
        time_split = namesplitted[-2]
        self._datetime = datetime.datetime( 2000+int(date_split[0:2]), int(date_split[2:4]), int(date_split[4:6]), int(time_split[0:2]), int(time_split[2:4]), int(time_split[4:6]) )

        # Load stimulus file
        self._matfile = loadmat(self._stimfile)

    # properties
    def __str__(self):
        """ Returns a printable string with summary output """
        return "StimulusData file {} from {}\n* Stim. dur={}s, iti={}s".format( self._stimfilename, self._datetime, self.stimulus_duration, self.iti_duration )

    @property
    def stimulus_duration(self):
        """ Returns a list with id's of the stimuli """
        return float(self._matfile['S']['StimulusDuration'][0,0])

    @property
    def iti_duration(self):
        """ Returns a list with id's of the stimuli """
        return float(self._matfile['S']['ITI'][0,0])

    @property
    def stimulus(self):
        """ Returns a list with id's of the stimuli """
        return self._matfile['S']['StimIDs'][0,0].ravel()

    @property
    def stimulus_ix(self):
        """ Returns a list with 'index' of the stimulus """
        (_,stimulus_ix) = np.unique(self.stimulus,return_inverse=True)
        return stimulus_ix

    @property
    def eye(self):
        """ Returns a list with eye-id's of the stimuli """
        return self._matfile['S']['EyeIDs'][0,0].ravel()

    @property
    def eye_ix(self):
        """ Returns a list with 'index' of the eye """
        (_,eye_ix) = np.unique(self.eye,return_inverse=True)
        return eye_ix

    @property
    def direction(self):
        """ Returns a list with directions of the stimuli """
        direction_list = self._matfile['S']['Angles'][0,0].ravel()
        return np.array(
            [direction_list[s_ix] for s_ix in self.stimulus_ix])

    @property
    def direction_id(self):
        """ Returns a list with the 'index' of stimulus direction """
        (_,direction_id) = np.unique(self.direction,return_inverse=True)
        return direction_id

    @property
    def spatialf(self):
        """ Returns a list with spatial frequencies of the stimuli """
        spatialf_list = self._matfile['S']['spatialF'][0,0].ravel()
        return np.array(
            [spatialf_list[s_ix] for s_ix in self.stimulus_ix])

    @property
    def spatialf_id(self):
        """ Returns a list with the 'index' of stimulus spatial frequency """
        (_,spatialf_id) = np.unique(self.spatialf,return_inverse=True)
        return spatialf_id

    @property
    def azimuth(self):
        """ Returns a list with azimuth of the stimuli """
        azimuth_list = self._matfile['S']['Azimuth'][0,0].ravel()
        return np.array(
            [azimuth_list[s_ix] for s_ix in self.stimulus_ix])

    @property
    def azimuth_id(self):
        """ Returns a list with the 'index' of stimulus azimuth """
        (_,azimuth_id) = np.unique(self.azimuth,return_inverse=True)
        return azimuth_id

    @property
    def elevation(self):
        """ Returns a list with elevation of the stimuli """
        elevation_list = self._matfile['S']['Elevation'][0,0].ravel()
        return np.array(
            [elevation_list[s_ix] for s_ix in self.stimulus_ix])

    @property
    def elevation_id(self):
        """ Returns a list with the 'index' of stimulus elevation """
        (_,elevation_id) = np.unique(self.elevation,return_inverse=True)
        return elevation_id
