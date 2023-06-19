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

    def __init__(self, filepath=".", filename=None, gonogo=False, task=False):
        """ - filepath: Path to where the .mat file is located
            - filename: Optional exact filename
        """

        # Find and load stimulus file
        super(StimulusData, self).__init__()

        # Get filename and store inputs
        if filename is None: filename = "*StimSettings.mat"
        self._stimfile = glob.glob( os.path.join(filepath,filename) )[0]
        self._stimfilename = self._stimfile.split(os.path.sep)[-1]

        # Set  stimulation metadata
        self._gonogo = gonogo
        self._task = task

        # Get date and time of the stimfile
        namesplitted = self._stimfilename.split("-")
        name_split = namesplitted[0]
        date_split = namesplitted[-(len(namesplitted)-1)]
        time_split = namesplitted[-(len(namesplitted)-2)]
        self._datetime = datetime.datetime( 2000+int(date_split[0:2]), int(date_split[2:4]), int(date_split[4:6]), int(time_split[0:2]), int(time_split[2:4]), np.min([int(time_split[4:6]),59]) )
        self._mousename = name_split

        # Load stimulus file
        self._matfile = loadmat(self._stimfile)

    # properties
    def __str__(self):
        """ Returns a printable string with summary output """
        if self.task:
            if self.gonogo:
                stimulustype = "Go/nogo task"
            else:
                stimulustype = "2AC task"
        else:
            stimulustype = "Passive stimulation"
        return "StimulusData file {} from {}\n* {}, stim. dur={}s, iti={}s".format( self._stimfilename, self.datetime, stimulustype, self.stimulus_duration, self.iti_duration )

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Stimulus metadata

    @property
    def task(self):
        """ Returns True when task, False for passive stimulation """
        return self._task

    @property
    def gonogo(self):
        """ Returns True when task is  go/nogo, False for 2AC """
        return self._gonogo

    @property
    def datetime(self):
        """ Returns date and time """
        return self._datetime

    @property
    def mousename(self):
        """ Returns the name of the mouse, from the filename """
        return self._mousename


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Stimulus parameters

    @property
    def stimulus_duration(self):
        """ Returns the preset duration of the stimuli """
        return float(self._matfile['S']['StimulusDuration'][0,0])

    @property
    def responsewindow_duration(self):
        """ Returns the preset duration of the stimuli """
        return float(self._matfile['S']['ResponseWindowTime'][0,0])

    @property
    def iti_duration(self):
        """ Returns the preset duration of the ITI """
        return float(self._matfile['S']['ITI'][0,0])


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Task parameters

    @property
    def response(self):
        """ Returns a list with id's of the responses
            Go/nogo: 1=go, 0=nogo
            2AC: 0=missed trial, 1=left, 2=right
        """
        if self.task:
            if self.gonogo:
                return self._matfile['MousesResponse'].ravel()
            else:
                return self._matfile['ResponseSide'].ravel()
        else:
            return None

    @property
    def outcome(self):
        """ Returns a list with id's of the outcome
            Go/nogo: 0=incorrect, 1=correct
            2AC: NaN= missed trial, 0=incorrect, 1=correct
        """
        if self.task:
            return self._matfile['Outcome'].ravel()
        else:
            return None

    @property
    def stimulus_on_timestamps(self):
        """ Returns a list with timestamps of stimulus onsets
        """
        if self.task:
            return self._matfile['StimOnset'].ravel()
        else:
            return None

    @property
    def lick_timestamps(self):
        """ Returns a list with timestamps of licks
        """
        if self.task:
            return self._matfile['LickTimeStamps'].ravel()
        else:
            return None

    @property
    def lick_directions(self):
        """ Returns a list with the direction of licks (1=left, 2=right)
        """
        if self.task:
            return self._matfile['LickDirection'].ravel()
        else:
            return None


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Stimulus identification

    @property
    def stimulus(self):
        """ Returns a list with id's of the stimuli """
        if self.task:
            return self._matfile['StimulusId'].ravel()
        else:
            return self._matfile['S']['StimIDs'][0,0].ravel()

    @property
    def stimulus_ix(self):
        """ Returns a list with the 'zero based index' of each stimulus """
        (_,stimulus_ix) = np.unique(self.stimulus,return_inverse=True)
        return stimulus_ix

    @property
    def category(self):
        """ Returns a list with id's of the category
            Go/nogo: 1=nogo, 2=go
            2AC: 1=left, 2=right
        """
        if self.task:
            return self._matfile['CategoryId'].ravel()

    @property
    def category_ix(self):
        """ Returns a list with 'index' of the category
            Go/nogo: 0=nogo, 1=go
            2AC: 0=left, 1=right
        """
        (_,category_ix) = np.unique(self.category,return_inverse=True)
        return category_ix

    @property
    def eye(self):
        """ Returns a list with eye-id's of the stimuli """
        if self.task:
            return None
        else:
            return self._matfile['S']['EyeIDs'][0,0].ravel()

    @property
    def eye_ix(self):
        """ Returns a list with 'index' of the eye """
        if self.task:
            return None
        else:
            (_,eye_ix) = np.unique(self.eye,return_inverse=True)
            return eye_ix

    @property
    def direction(self):
        """ Returns a list with directions of the stimuli (on range of 0 to 360 degrees) """
        if self.task:
            if self.gonogo:
                direction_list = [self._matfile['S']['Cat1'][0,0]['Angles'][0,0].ravel(), self._matfile['S']['Cat2'][0,0]['Angles'][0,0].ravel()]
            else:
                direction_list = [self._matfile['S']['LeftCat'][0,0]['Angles'][0,0].ravel(), self._matfile['S']['RightCat'][0,0]['Angles'][0,0].ravel()]
            return np.array(
                [direction_list[c][s] for c,s in zip(self.category_ix,self.stimulus_ix)] )
        else:
            direction_list = self._matfile['S']['Angles'][0,0].ravel()
            return np.array(
                [direction_list[s_ix] for s_ix in self.stimulus_ix])

    @property
    def direction_id(self):
        """ Returns a list with the 'index' of stimulus direction """
        (_,direction_id) = np.unique(self.direction,return_inverse=True)
        return direction_id

    @property
    def orientation(self):
        """ Returns a list with orientations of the stimuli (on range of 0 to 180 degrees) """
        return np.mod(self.direction,180)

    @property
    def orientation_id(self):
        """ Returns a list with the 'index' of stimulus orientation """
        (_,orientation_id) = np.unique(self.orientation,return_inverse=True)
        return orientation_id

    @property
    def spatialf(self):
        """ Returns a list with spatial frequencies of the stimuli """
        if self.task:
            if self.gonogo:
                spatialf_list = [self._matfile['S']['Cat1'][0,0]['spatialF'][0,0].ravel(), self._matfile['S']['Cat2'][0,0]['spatialF'][0,0].ravel()]
            else:
                spatialf_list = [self._matfile['S']['LeftCat'][0,0]['spatialF'][0,0].ravel(),self._matfile['S']['RightCat'][0,0]['spatialF'][0,0].ravel()]
            return np.array(
                [spatialf_list[c][s] for c,s in zip(self.category_ix,self.stimulus_ix)] )
        else:
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
        if self.task:
            if self.gonogo:
                spatialf_list = [self._matfile['S']['Cat1'][0,0]['Azimuth'][0,0].ravel(), self._matfile['S']['Cat2'][0,0]['Azimuth'][0,0].ravel()]
            else:
                spatialf_list = [self._matfile['S']['LeftCat'][0,0]['Azimuth'][0,0].ravel(),self._matfile['S']['RightCat'][0,0]['Azimuth'][0,0].ravel()]
            return np.array(
                [spatialf_list[c][s] for c,s in zip(self.category_ix,self.stimulus_ix)] )
        else:
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
        if self.task:
            if self.gonogo:
                spatialf_list = [self._matfile['S']['Cat1'][0,0]['Elevation'][0,0].ravel(), self._matfile['S']['Cat2'][0,0]['Elevation'][0,0].ravel()]
            else:
                spatialf_list = [self._matfile['S']['LeftCat'][0,0]['Elevation'][0,0].ravel(),self._matfile['S']['RightCat'][0,0]['Elevation'][0,0].ravel()]
            return np.array(
                [spatialf_list[c][s] for c,s in zip(self.category_ix,self.stimulus_ix)] )
        else:
            elevation_list = self._matfile['S']['Elevation'][0,0].ravel()
            return np.array(
                [elevation_list[s_ix] for s_ix in self.stimulus_ix])

    @property
    def elevation_id(self):
        """ Returns a list with the 'index' of stimulus elevation """
        (_,elevation_id) = np.unique(self.elevation,return_inverse=True)
        return elevation_id
