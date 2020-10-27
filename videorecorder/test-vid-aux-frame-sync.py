#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

This script tests the synchronization of video frames to the auxrecorder

Created on Saturday 24 Oct 2020

/Volumes/PG-Data/Data/test-eyetrack

@author: pgoltstein
"""

import os, glob, sys
import matplotlib.pyplot as plt
sys.path.append('../auxrecorder')
import auxrec
import vidrec
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import cv2
from tqdm import tqdm
#from tqdm import tqdm
import argparse

# settings for retaining pdf font
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
matplotlib.rcParams['font.sans-serif'] = "Arial"
matplotlib.rcParams['font.family'] = "sans-serif"

# Default settings
font_size = { "title": 10, "label": 9, "tick": 9, "text": 8, "legend": 8 }

# seaborn color context (all to black)
color_context = {   'axes.edgecolor': '#000000',
                    'axes.labelcolor': '#000000',
                    'boxplot.capprops.color': '#000000',
                    'boxplot.flierprops.markeredgecolor': '#000000',
                    'grid.color': '#000000',
                    'patch.edgecolor': '#000000',
                    'text.color': '#000000',
                    'xtick.color': '#000000',
                    'ytick.color': '#000000'}


#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# Arguments

parser = argparse.ArgumentParser( description = "This script tests the syncronization of video frames to 'aux recorded' trials.\n (written by Pieter Goltstein - Oct 2020)")
parser.add_argument('filepath', type=str, help= 'path to the folder holding the lvd and .vid file')
parser.add_argument('-f', '--filestem', type=str, default="", help='filestem for selecting matching aux, lvd and eye files')
parser.add_argument('-n', '--nimagingplanes',  type=int, help='Number of imaging planes acquired in fast z-stack (default=1)', default=1)
args = parser.parse_args()

# process arguments
filepath = args.filepath
if filepath[-1] == '"':
    filepath = filepath[:-1]
filestem = args.filestem
n_imaging_planes = args.nimagingplanes


#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# functions

def init_figure_axes( fig_size=(10,7), dpi=80, facecolor="w", edgecolor="w" ):
    # Convert fig size to inches (default is inches, fig_size argument is supposed to be in cm)
    inch2cm = 2.54
    fig_size = fig_size[0]/inch2cm,fig_size[1]/inch2cm
    with sns.axes_style(style="ticks",rc=color_context):
        fig,ax = plt.subplots(num=None, figsize=fig_size, dpi=dpi,
            facecolor=facecolor, edgecolor=edgecolor)
        return fig,ax

def finish_figure( filename=None, wspace=None, hspace=None ):
    """ Finish up layout and save to ~/figures"""
    plt.tight_layout()
    if wspace is not None or hspace is not None:
        if wspace is None: wspace = 0.6
        if hspace is None: hspace = 0.8
        plt.subplots_adjust( wspace=wspace, hspace=hspace )
    if filename is not None:
        plt.savefig(filename+'.pdf', transparent=True)


#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# Code

# Load Aux data
auxfilestem = "*"+filestem+"*.lvd"
Aux = auxrec.LvdAuxRecorder(args.filepath, filename=auxfilestem, nimagingplanes=n_imaging_planes)
print(Aux)

datatype = "vid" # vid, eye1, eye2

# Load Vid data
if datatype == "vid":
    vidfilestem = "*"+filestem+"*.vid"
    Video = vidrec.VidRecording(args.filepath, filename=vidfilestem, verbose=False)
    print(Video)

    # Load Vid synchronization indices
    search_path = os.path.join(args.filepath,"*"+filestem+"*vid-ix.npy")
    ix_files_full = glob.glob(search_path)
    sync_ixs = np.load(ix_files_full[0], allow_pickle=True).item()["video_frame_conversion_index"].astype(int)
else:
    # Load eye data
    eyefilestem = "*"+filestem+"*."+datatype
    Video = vidrec.EyeRecording(args.filepath, filename=eyefilestem, verbose=False)
    print(Video)

    # Load Vid synchronization indices
    search_path = os.path.join(args.filepath,"*"+filestem+"*"+datatype+"-ix.npy")
    ix_files_full = glob.glob(search_path)
    sync_ixs = np.load(ix_files_full[0], allow_pickle=True).item()["video_frame_conversion_index"].astype(int)

# Find visual stimulus onsets in aux data
stim_onsets = Aux.stimulus_onsets

# show 10 frames around stimulus onset for the 10 first trials
use_trials = np.arange(1,100,10).astype(int)
use_frames = np.arange(-1,11).astype(int)
n_frames_to_load = len(use_trials)*len(use_frames)
fig,ax = init_figure_axes(fig_size=(len(use_frames)*2,len(use_trials)*1.8))
with tqdm(total=n_frames_to_load, desc="Reading/processing", unit="Fr") as bar:
    for tr_cnt,tr in enumerate(use_trials):
        for fr_cnt,fr in enumerate(use_frames):
            ax = plt.subplot2grid( (len(use_trials),len(use_frames)), (tr_cnt,fr_cnt) )
            imaging_frame = stim_onsets[tr]+fr
            video_frame = sync_ixs[imaging_frame]
            image = Video[video_frame][:,:,0]
            plt.imshow(image, cmap='gray', vmin=0, vmax=255)
            plt.axis('off')
            if fr_cnt == 0:
                plt.title("Trial {}".format(tr), fontsize=8)
            if fr_cnt == 2:
                plt.title("on ->", fontsize=8)
            bar.update(1)
finish_figure( filename=os.path.join("/Users/pgoltstein/figures",filestem+"-example-"+datatype+"-sync"), wspace=0.1, hspace=0.4 )


#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# That's all folks!
plt.show()
