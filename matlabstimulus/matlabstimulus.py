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


    # properties
    def __str__(self):
        """ Returns a printable string with summary output """
        return "StimulusData file {} from {}\n* # of stimuli: {}".format( self._stimfilename, self._datetime, 0 )
