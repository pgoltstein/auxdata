#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

This script finds eye movies in the supplied directory and converts them to a platform compatible video file

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

parser = argparse.ArgumentParser( description = "This script finds .eye movies in the supplied directory and converts them to a platform compatible video file.\n (written by Pieter Goltstein - July 2020)")
parser.add_argument('filepath', type=str, help= 'path to the folder holding the .eye1 and .eye2 files')
parser.add_argument('-o', '--overwrite',  action="store_true", default=False, help='Enables to overwrite existing files')
args = parser.parse_args()

# process arguments
filepath = args.filepath
if filepath[-1] == '"':
    filepath = filepath[:-1]
overwrite_old_files = args.overwrite


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

def export_eye_movie( filepath, eyemovie_filename, target_filename, overwrite_existing=False):
    """ Loads the eyemovie and saves to target video
    """

    # Open eye movie
    Eye = vidrec.EyeRecording(filepath, filename=eyemovie_filename, verbose=True)
    print(Eye)

    # Check if old target file is present
    target_video_file_name = os.path.join(filepath,target_filename)
    if os.path.isfile(target_video_file_name):
        if overwrite_existing:
            print("Deleting old file: {}".format(target_video_file_name))
            os.remove(target_video_file_name)
        else:
            print("Skipping because target file is already present:\n {}\n".format(target_video_file_name))
            return None

    # Load eye movie data
    eyemovie = Eye[:100]

    # Create video file object
    fourcc = cv2.VideoWriter_fourcc(*codec)
    video_object = cv2.VideoWriter( target_video_file_name, fourcc, 30.0, (Eye.xres,Eye.yres) )

    # Write movie
    print("Target file: {}".format(eye_target))
    with tqdm(total=eyemovie.shape[2], desc="Writing", unit="Fr") as bar:
        for fr in range(eyemovie.shape[2]):
            frame = eyemovie[:,:,fr]
            frame = np.repeat(frame[:,:,np.newaxis],3,axis=2)
            video_object.write(frame)
            bar.update(1)

    video_object.release()


# =============================================================================
# Main

# Find eye files and convert
eye_source_filenames,eye_target_filenames = find_eye_files(filepath)
for eye_source,eye_target in zip(eye_source_filenames,eye_target_filenames):

    print("\n--- exporting eye-movie ---\nBase path:{}".format(filepath))

    # Read eyemovie and write video
    export_eye_movie( filepath, eye_source, eye_target, overwrite_existing=overwrite_old_files)



#++
