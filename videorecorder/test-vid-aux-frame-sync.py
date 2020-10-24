#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

This script tests the synchronization of video frames to the auxrecorder

Created on Saturday 24 Oct 2020

@author: pgoltstein
"""

import os, glob, sys
import matplotlib.pyplot as plt
import vidrec
import numpy as np
import cv2
#from tqdm import tqdm
import argparse


#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# Arguments

parser = argparse.ArgumentParser( description = "This script tests the syncronization of video frames to 'aux recorded' trials.\n (written by Pieter Goltstein - Oct 2020)")
parser.add_argument('filepath', type=str, help= 'path to the folder holding the lvd and .vid file')
parser.add_argument('-n', '--nimagingplanes',  type=int, help='Number of imaging planes acquired in fast z-stack (default=1)', default=1)
args = parser.parse_args()

# process arguments
filepath = args.filepath
if filepath[-1] == '"':
    filepath = filepath[:-1]
n_imaging_planes = args.nimagingplanes

#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# Code

# Load Aux data
Aux = auxrec.LvdAuxRecorder(args.filepath, nimagingplanes=n_imaging_planes)
print(Aux)

# Get timestamps (in seconds) for frame onsets
frameonsets = Aux.imagingframes
frameonset_ts = (frameonsets / Aux.sf).ravel()
video_vs_aux_start_offset,_ = Aux.shuttertimestamps
