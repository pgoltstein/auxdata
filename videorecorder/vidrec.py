#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Script to load eye and video files from two-photon setups, labview based binary files

Created on Fri July 17, 2020

@author: pgoltstein
"""

# Imports
import os, glob
import datetime
import numpy as np
from tqdm import tqdm


#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# Classes

class EyeRecording(object):
    """ Loads and represents eye movie data.
    """

    def __init__(self, filepath=".", eyeid=1, verbose=True):
        """ - filepath: Path to where the eye movie videofiles are located
            - eyeid: 1, 2 (for eye1, eye2)
        """

        # Find and load movie file
        super(EyeRecording, self).__init__()

        # Get filename and store inputs
        filename = "*.eye" + str(int(eyeid))
        self._eyefile = glob.glob( os.path.join(filepath,filename) )[0]
        self._eyefilename = self._eyefile.split(os.path.sep)[-1]
        self._verbose = verbose

        # Open the aux file for reading
        with open(self._eyefile, 'rb') as f:

            # Reset file index
            f.seek(0)

            # Get meta data
            self._metadata_size = 9
            self._metadata = np.fromfile(f, dtype='>f8', count=self._metadata_size)
            self._xres = int(self._metadata[4]-self._metadata[2])
            self._yres = int(self._metadata[5]-self._metadata[3])


            # Calculate number of frames
            filesize = os.stat(self._eyefile).st_size
            self._nframes = int(filesize / ((self.xres*self.yres)+(self._metadata_size*8)))

    # properties
    def __str__(self):
        """ Returns a printable string with summary output """
        return "EyeRecording: {}\n* {} frames, {} x {} pixels".format( self._eyefilename, self.nframes, self.yres, self.xres )

    @property
    def xres(self):
        """ Number of pixels along the x-axis """
        return self._xres

    @property
    def yres(self):
        """ Number of pixels along the y-axis """
        return self._yres

    @property
    def resolution(self):
        """ Number of pixels along the y- and x-axis """
        return self._yres,self._xres

    @property
    def nframes(self):
        """ Number of frames """
        return self._nframes

    # Internal function to load the movie data using slicing
    def __getitem__(self, indices):
        """ Loads and returns the eye movie data directly from disk """

        # Use the provided slice object to get the requested frames
        if isinstance(indices, slice):
            frames = np.arange(self.nframes)[indices]
        elif isinstance(indices, list) or isinstance(indices, tuple):
            frames = np.array(indices)
        else:
            frames = np.array([indices,])

        frame_step = ((self.xres*self.yres)+(self._metadata_size*8))
        frame_size = self.xres*self.yres
        frame_ixs = (frames * frame_step) + (self._metadata_size*8)
        n_frame_ixs = len(frame_ixs)

        # Check if continuous block of frames
        moviedata = np.zeros((self.yres,self.xres,n_frame_ixs),dtype=np.uint8)
        if self._verbose:
            with tqdm(total=n_frame_ixs, desc="Reading", unit="Fr") as bar:
                with open(self._eyefile, 'rb') as f:
                    for fr_nr,fr_ix in enumerate(frame_ixs):
                        f.seek(fr_ix)
                        frame = np.reshape( np.fromfile(f, dtype='>u1', count=frame_size), (self.yres,self.xres) )
                        moviedata[:,:,fr_nr] = frame
                        bar.update(1)
        else:
            with open(self._eyefile, 'rb') as f:
                for fr_nr,fr_ix in enumerate(frame_ixs):
                    f.seek(fr_ix)
                    frame = np.reshape( np.fromfile(f, dtype='>u1', count=frame_size), (self.yres,self.xres) )
                    moviedata[:,:,fr_nr] = frame
        return moviedata
