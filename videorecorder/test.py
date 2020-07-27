#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

This script tests the module videorecorder.
if ffmpeg gives lots of text output:
    export FFREPORT=level=quiet

Created on Thursday 16 July 2020

@author: pgoltstein
"""

import os, glob, sys
import matplotlib.pyplot as plt
import vidrec
import numpy as np
import cv2
#from tqdm import tqdm
import argparse


# =============================================================================
# Arguments

parser = argparse.ArgumentParser( description = "This script tests the module video recorder.\n (written by Pieter Goltstein - July 2020)")
parser.add_argument('filepath', type=str, help= 'path to the folder holding the lvd, .eye1, .eye2 and .vid file')
args = parser.parse_args()


# =============================================================================
# Code


print("\nTesting videorecorder:")
Eye1 = vidrec.EyeRecording(args.filepath, eyeid=1, verbose=True)
print(Eye1)

print("\nTest loading frames")
datablock = Eye1[500:1000]
#video_file_name = os.path.join(args.filepath,'eye2.mov')
#fourcc = cv2.VideoWriter_fourcc(*'avc1')

# !!! try with 640x480 sized images

print("\nTesting videorecorder:")
Vid = vidrec.VidRecording(args.filepath, filename=None, verbose=True)
print(Vid)

timestamps1 = Eye1.timestamps
print(timestamps1[0])
print(timestamps1[1])
plt.plot(timestamps1-timestamps1[0])
timestamps2 = Vid.timestamps
print(timestamps2[0])
print(timestamps2[1])
plt.plot(timestamps2-timestamps2[0])
plt.show()

# video_file_name = os.path.join(args.filepath,'eye1.avi')
# fourcc = cv2.VideoWriter_fourcc(*'divx')
# video_object = cv2.VideoWriter( video_file_name, fourcc, 30.0, (Eye1.xres,Eye1.yres) )
# # video_object = cv2.VideoWriter( video_file_name, fourcc, 30.0, (640,480) )
#
# print(datablock.shape)
# print(Eye1.xres,Eye1.yres)

# with tqdm(total=datablock.shape[2], desc="Writing", unit="Fr") as bar:
    # for fr in range(datablock.shape[2]):
        # video_object.write(datablock[:,:,fr])
        # bar.update(1)

# # for fr in range(255):
# for fr in range(datablock.shape[2]):
#     # frame = np.zeros((480,640,3)).astype(np.uint8)+fr
#     frame = datablock[:,:,fr]
#     frame = np.repeat(frame[:,:,np.newaxis],3,axis=2)
#     print(frame.dtype)
#     print(frame.shape)
#     video_object.write(frame)
#
#     # video_object.write(datablock[:,:,fr].T)
# video_object.release()

# Set up video file
# video_file_name = os.path.join(args.filepath,'eye1.mov')
# fourcc = cv2.VideoWriter_fourcc(*'avc1')
# video_object = cv2.VideoWriter( video_file_name,fourcc, 30.0, (Eye1.xres,Eye1.yres) )

# # Playback movie
# for fr in range(Vid.nframes):
#     frame = Vid[fr]
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
