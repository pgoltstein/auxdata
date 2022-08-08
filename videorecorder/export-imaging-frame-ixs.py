#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

This script finds aux, eye and vid movies in the supplied directory, gets the movie timestamps and imaging frame timestamps, and stores a numpy or matlab file that holds the nearest video-index for each imaging frame

Created on Sunday 2 August 2020

@author: pgoltstein
"""

import os, glob, sys
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import savemat
if "darwin" in sys.platform.lower(): # MAC OS X
    sys.path.append('../auxrecorder')
    sys.path.append('../videorecorder')
elif "win" in sys.platform.lower(): # Windows
    sys.path.append('D:/code/auxdata/auxrecorder')
    sys.path.append('D:/code/auxdata/videorecorder')
import auxrec
import vidrec
import argparse


# =============================================================================
# Arguments

parser = argparse.ArgumentParser( description = "This script finds aux, eye and vid movies in the supplied directory, gets the movie timestamps and imaging frame timestamps, and stores a numpy or matlab file that holds the nearest video-index for each imaging frame.\n (written by Pieter Goltstein - August 2020)")
parser.add_argument('filepath', type=str, help= 'path to the folder holding the .lvd, .vid, .eye1 and .eye2 files')
parser.add_argument('settingsfile', type=str, help= 'path to the folder holding the aux-settings file')
parser.add_argument('-f', '--filestem', type=str, default="", help='filestem for selecting matching aux, lvd and eye files')
parser.add_argument('-o', '--overwrite',  action="store_true", default=False, help='Enables to overwrite existing files')
parser.add_argument('-m', '--matlab',  action="store_true", default=False, help='Stores data as .mat file')
parser.add_argument('-fus', '--functionalultrasoundimaging',  action="store_true", default=False, help='Imaging triggers from functional ultrasound imaging setup (as opposed to two-photon imaging setup)')
parser.add_argument('-n', '--nimagingplanes',  type=int, help='Number of imaging planes acquired in fast z-stack (default=1)', default=1)
args = parser.parse_args()

# process arguments
filepath = args.filepath
if filepath[-1] == '"':
    filepath = filepath[:-1]
filestem = args.filestem
overwrite_old_files = args.overwrite
store_as_matlab = args.matlab
n_imaging_planes = args.nimagingplanes
fusimaging = args.functionalultrasoundimaging

# =============================================================================
# Functions

def find_eye_files(path, filestem):
    """ Returns a list with full filenames, and their conversion filenames
    """
    search_path = os.path.join(path,"*"+filestem+"*.eye*")
    eye_files_full = glob.glob(search_path)
    eye_source_filenames = []
    frameindex_target_filenames = []
    for eye_file in eye_files_full:
        eye_filename = eye_file.split(os.path.sep)[-1]
        target_name = eye_filename[:-5]+"-"+eye_filename[-4:]+"-ix"
        eye_source_filenames.append(eye_filename)
        frameindex_target_filenames.append(target_name)
    return eye_source_filenames, frameindex_target_filenames

def find_vid_files(path, filestem):
    """ Returns a list with full filenames, and their conversion filenames
    """
    search_path = os.path.join(path,"*"+filestem+"*.vid")
    vid_files_full = glob.glob(search_path)
    vid_source_filenames = []
    frameindex_target_filenames = []
    for vid_file in vid_files_full:
        vid_filename = vid_file.split(os.path.sep)[-1]
        target_name = vid_filename[:-4]+"-"+vid_filename[-3:]+"-ix"
        vid_source_filenames.append(vid_filename)
        frameindex_target_filenames.append(target_name)
    return vid_source_filenames, frameindex_target_filenames


def check_and_remove_file_already_present( filepath, target_filename, store_as_matlab=False, overwrite_existing=False ):
    """ Check if old target file is present and delete it when the flag is set
    """
    target_file_name = os.path.join(filepath,target_filename)
    if store_as_matlab:
        target_file_name += ".mat"
    else:
        target_file_name += ".npy"
    if os.path.isfile(target_file_name):
        if overwrite_existing:
            print("Deleting old file: {}".format(target_file_name))
            os.remove(target_file_name)
            return True
        else:
            print("Skipping because target file is already present:\n {}\n".format(target_file_name))
            return False
    else:
        return True


def export_video_index( imageframe_ts, videoframe_ts, filepath, export_filename, store_as_matlab ):
    """ Calculates the index to get 1 video frame per imaging frame and exports it to a file (.npy or .mat)
    """

    video_conversion_index = np.zeros_like(imageframe_ts)
    for nr,im_ts in enumerate(imageframe_ts):
        video_conversion_index[nr] = np.argmin(np.abs(videoframe_ts-im_ts))

    # print(videoframe_ts[0])
    # print(imageframe_ts[0])
    # print("nr={:4.0f}, frame index={:5.0f}".format( 0, video_conversion_index[0] ))
    #
    # print(videoframe_ts[-1])
    # print(imageframe_ts[-1])
    # print("nr={:4.0f}, frame index={:5.0f}".format( nr, video_conversion_index[nr] ))

    # Save index to file
    export_file_name = os.path.join(filepath,export_filename)
    if store_as_matlab:
        savemat(export_file_name, {"VideoFrameConversionIndex": video_conversion_index} )
        print("Exported VideoFrameIndex to: \n{}".format( export_file_name+".mat" ))
    else:
        np.save(export_file_name,{"video_frame_conversion_index": video_conversion_index})
        print("Exported VideoFrameIndex to: \n{}".format( export_file_name+".npy" ))


# =============================================================================
# Main

print("\n--- calculating frame indices for eye and vid movies ---\nBase path:{}".format(filepath))

# Load Aux data
auxfilestem = "*"+filestem+"*.lvd"
Aux = auxrec.LvdAuxRecorder(args.filepath, filename=auxfilestem, auxsettingsfile=args.settingsfile, nimagingplanes=n_imaging_planes, fUS=fusimaging)
print(Aux)

# Get timestamps (in seconds) for frame onsets
frameonsets = Aux.imagingframes
frameonset_ts = (frameonsets / Aux.sf).ravel()
video_vs_aux_start_offset,_ = Aux.shuttertimestamps

# Find eye files and convert
eye_source_filenames, frameindex_target_filenames = find_eye_files(filepath,filestem)
for eye_source, frameindex_target in zip(eye_source_filenames,frameindex_target_filenames):

    # First check if file was not already exported
    if check_and_remove_file_already_present( filepath, frameindex_target, store_as_matlab, overwrite_old_files ):

        # Open .eye movie
        Eye = vidrec.EyeRecording(filepath, filename=eye_source, verbose=True)
        print(Eye)

        # Get frame timestamps (in seconds), from the first imaging frame onwards
        video_ts = Eye.timestamps
        video_ts = ((video_ts - video_ts[0]) / 1000).ravel()

        # The video start at the first imaging frame, while the aux recorder starts earlier, so correct the video timestamps for that
        video_ts = video_ts + video_vs_aux_start_offset

        # Calculate the video frame index and export to file
        export_video_index( imageframe_ts=frameonset_ts, videoframe_ts=video_ts, filepath=filepath, export_filename=frameindex_target, store_as_matlab=store_as_matlab )

# Find .vid files and convert
vid_source_filenames,vid_target_filenames = find_vid_files(filepath,filestem)
for vid_source,frameindex_target in zip(vid_source_filenames,vid_target_filenames):

    # First check if file was not already exported
    if check_and_remove_file_already_present( filepath, frameindex_target, store_as_matlab, overwrite_old_files ):

        # Open .vid movie
        Vid = vidrec.VidRecording(filepath, filename=vid_source, verbose=True)
        print(Vid)

        # Get frame timestamps (in seconds), from the first imaging frame onwards
        video_ts = Vid.timestamps
        video_ts = ((video_ts - video_ts[0]) / 1000).ravel()

        # The video start at the first imaging frame, while the aux recorder starts earlier, so correct the video timestamps for that
        video_ts = video_ts + video_vs_aux_start_offset

        # Calculate the video frame index and export to file
        export_video_index( imageframe_ts=frameonset_ts, videoframe_ts=video_ts, filepath=filepath, export_filename=frameindex_target, store_as_matlab=store_as_matlab )


#++
