#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

This script finds eyemovies in the supplied directory and converts them to a platform compatible video file

Created on Sunday 19 July 2020

@author: pgoltstein
"""

import os, glob
import matplotlib.pyplot as plt
import vidrec
import numpy as np
import cv2
import warnings
from tqdm import tqdm
from sys import platform as _platform
import argparse

# Probably shouldn't do this, but got tired of "mean of empty slice" warnings
warnings.filterwarnings('ignore')


# =============================================================================
# Detect operating system

if "linux" in _platform.lower():
   OS = "linux" # linux
   sys_vid_ext = "avi"
   codec = "MJPG"
elif "darwin" in _platform.lower():
   OS = "macosx" # MAC OS X
   sys_vid_ext = "mov"
   codec = "avc1"
elif "win" in _platform.lower():
   OS = "windows" # Windows
   sys_vid_ext = "avi"
   codec = "divx"


# =============================================================================
# Arguments

parser = argparse.ArgumentParser( description = "This script finds eyemovies in the supplied directory and converts them to a platform compatible video file.\n (written by Pieter Goltstein - July 2020)")
parser.add_argument('filepath', type=str, help= 'path to the folder holding the .eye1 and .eye2 files')
args = parser.parse_args()

# process arguments
filepath = args.filepath
if filepath[-1] == '"':
    filepath = filepath[:-1]


# =============================================================================
# Functions

def find_eye_files(path):
    """ Returns a list with full filenames, and their conversion filenames
    """
    search_path = os.path.join(path,"*.eye*")
    eye_files_full = glob.glob(search_path)
    eye_source_filenames = []
    video_target_filenames = []
    for eye_file in eye_files_full:
        eye_filename = eye_file.split(os.path.sep)[-1]
        target_name = eye_filename[:-5]+"-"+eye_filename[-4:]+"."+sys_vid_ext
        eye_source_filenames.append(eye_filename)
        video_target_filenames.append(target_name)
    return eye_source_filenames, video_target_filenames

def export_eye_movie( filepath, eyemovie_filename, target_filename):
    """ Loads the eyemovie and saves to target video
    """

    # Load eye movie
    Eye = vidrec.EyeRecording(filepath, filename=eyemovie_filename, verbose=True)
    print(Eye)
    eyemovie = Eye[500:1000]

    # Create video file object
    video_file_name = os.path.join(filepath,target_filename)
    fourcc = cv2.VideoWriter_fourcc(*codec)
    video_object = cv2.VideoWriter( video_file_name, fourcc, 30.0, (Eye.xres,Eye.yres) )

    # Write movie
    with tqdm(total=eyemovie.shape[2], desc="Writing", unit="Fr") as bar:
        for fr in range(eyemovie.shape[2]):
            frame = eyemovie[:,:,fr]
            frame = np.repeat(frame[:,:,np.newaxis],3,axis=2)
            video_object.write(frame)
            bar.update(1)

    video_object.release()


# =============================================================================
# Main

# Find files and produce target file names
eye_source_filenames,video_target_filenames = find_eye_files(filepath)

# Loop files
for eye_source,eye_target in zip(eye_source_filenames,video_target_filenames):

    print("\n\n--- {} ---".format(eye_source))
    print("Target: {}\n".format(eye_target))

    # Read eyemovie and write video
    export_eye_movie( filepath, eye_source, eye_target)





#++