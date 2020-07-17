#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

This script tests the module videorecorder.
if ffmpeg gives lots of text output:
    export FFREPORT=level=quiet

Created on Thursday 16 July 2020

@author: pgoltstein
"""

import os, glob
import matplotlib.pyplot as plt
import vidrec
import numpy as np
import cv2
from tqdm import tqdm
import argparse


# =============================================================================
# Arguments

parser = argparse.ArgumentParser( description = "This script tests the module video recorder.\n (written by Pieter Goltstein - July 2020)")
parser.add_argument('filepath', type=str, help= 'path to the folder holding the .eye1, .eye2 and .vid file')
args = parser.parse_args()


# =============================================================================
# Code


print("\nTesting videorecorder:")
Eye1 = vidrec.EyeRecording(args.filepath, eyeid=2, verbose=True)
print(Eye1)

print("\nTest loading frames")
datablock = Eye1[::50]
video_file_name = os.path.join(args.filepath,'eye2.mov')
fourcc = cv2.VideoWriter_fourcc(*'avc1')
video_object = cv2.VideoWriter( video_file_name,fourcc, 30.0, (Eye1.xres,Eye1.yres) )

with tqdm(total=datablock.shape[2], desc="Writing", unit="Fr") as bar:
    for fr in range(datablock.shape[2]):
        video_object.write(datablock[:,:,fr])
        bar.update(1)

video_object.release()

# Set up video file
# video_file_name = os.path.join(args.filepath,'eye1.mov')
# fourcc = cv2.VideoWriter_fourcc(*'avc1')
# video_object = cv2.VideoWriter( video_file_name,fourcc, 30.0, (Eye1.xres,Eye1.yres) )

# # Playback movie
# for fr in range(Eye1.nframes):
#     frame = Eye1[fr]
#     cv2.imshow('frame',frame)
#
#     # video_object.write(frame)
#
#     # Exit if ESC pressed
#     try:
#         k = cv2.waitKey(1) & 0xff
#         if k == 27 : break
#     except:
#         pass

# Release video file
# video_object.release()

print("\nDone testing\n")
