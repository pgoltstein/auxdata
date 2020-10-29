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
if "darwin" in sys.platform.lower(): # MAC OS X
    sys.path.append('../auxrecorder')
elif "win" in sys.platform.lower(): # Windows
    sys.path.append('D:/code/auxdata/auxrecorder')
import auxrec
import vidrec
import numpy as np
import pandas as pd
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
parser.add_argument('-d', '--datatype', type=str, default="eye1", help='vid, eye1, eye2 for selecting each file')
parser.add_argument('-n', '--nimagingplanes',  type=int, help='Number of imaging planes acquired in fast z-stack (default=1)', default=1)
args = parser.parse_args()

# process arguments
filepath = args.filepath
if filepath[-1] == '"':
    filepath = filepath[:-1]
filestem = args.filestem
n_imaging_planes = args.nimagingplanes
datatype = args.datatype


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

def finish_panel( ax, title="", ylabel="", xlabel="", legend="off", y_minmax=None, y_step=None, y_margin=0.02, y_axis_margin=0.01, x_minmax=None, x_step=None, x_margin=0.55, x_axis_margin=0.55, x_ticks=None, x_ticklabels=None, y_ticks=None, y_ticklabels=None, x_tick_rotation=0, tick_size=None, label_size=None, title_size=None, legend_size=None, despine=True, legendpos=0):
    """ Finished axis formatting of an individual plot panel """
    if tick_size is None: tick_size=font_size['tick']
    if label_size is None: label_size=font_size['label']
    if title_size is None: title_size=font_size['title']
    if legend_size is None: legend_size=font_size['legend']

    # Set limits and trim spines
    if y_minmax is not None:
        ax.set_ylim(y_minmax[0]-y_margin,y_minmax[1]+y_margin)
    if x_minmax is not None:
        ax.set_xlim(x_minmax[0]-x_margin,x_minmax[-1]+x_margin)
    if despine:
        sns.despine(ax=ax, offset=0, trim=True)

    # Set tickmarks and labels
    if x_ticklabels is not None:
        plt.xticks( x_ticks, x_ticklabels, rotation=x_tick_rotation, fontsize=tick_size )
    elif x_minmax is not None and x_step is not None:
        plt.xticks( np.arange(x_minmax[0],x_minmax[1]+0.0000001,x_step[0]), suck_on_that_0point0(x_minmax[0], x_minmax[1]+0.0000001, step=x_step[0], format_depth=x_step[1]), rotation=x_tick_rotation, fontsize=tick_size )
    if y_ticklabels is not None:
        plt.yticks( y_ticks, y_ticklabels, fontsize=tick_size )
    elif y_minmax is not None and y_step is not None:
        plt.yticks( np.arange(y_minmax[0],y_minmax[1]+0.0000001,y_step[0]), suck_on_that_0point0(y_minmax[0], y_minmax[1]+0.0000001, step=y_step[0], format_depth=y_step[1]), rotation=0, fontsize=tick_size )

    ax.tick_params(length=3)

    # Set spine limits
    if y_minmax is not None:
        ax.spines['left'].set_bounds( y_minmax[0]-y_axis_margin, y_minmax[1]+y_axis_margin )
    if x_minmax is not None:
        ax.spines['bottom'].set_bounds( x_minmax[0]-x_axis_margin, x_minmax[1]+x_axis_margin )

    # Add title and legend
    if title != "":
        plt.title(title, fontsize=title_size)
    if ylabel != "":
        plt.ylabel(ylabel, fontsize=label_size)
    if xlabel != "":
        plt.xlabel(xlabel, fontsize=label_size)
    if legend == "on":
        lgnd = plt.legend(loc=legendpos, fontsize=legend_size, ncol=1, frameon=True)
        lgnd.get_frame().set_facecolor('#ffffff')

def finish_figure( filename=None, wspace=None, hspace=None ):
    """ Finish up layout and save to ~/figures"""
    plt.tight_layout()
    if wspace is not None or hspace is not None:
        if wspace is None: wspace = 0.6
        if hspace is None: hspace = 0.8
        plt.subplots_adjust( wspace=wspace, hspace=hspace )
    if filename is not None:
        plt.savefig(filename+'.pdf', transparent=True)

def suck_on_that_0point0( start, stop, step=1, format_depth=1, labels_every=None ):
    values = []
    if labels_every is None:
        values = []
        for i in np.arange( start, stop, step ):
            if i == 0:
                values.append('0')
            else:
                values.append('{:0.{dpt}f}'.format(i,dpt=format_depth))
    else:
        for i in np.arange( start, stop, step ):
            if i == 0 and np.mod(i,labels_every)==0:
                values.append('0')
            elif np.mod(i,labels_every)==0:
                values.append('{:0.{dpt}f}'.format(i,dpt=format_depth))
            else:
                values.append('')
    return values

def mean_sem( datamat, axis=0 ):
    mean = np.nanmean(datamat,axis=axis)
    n = np.sum( ~np.isnan( datamat ), axis=axis )
    sem = np.nanstd( datamat, axis=axis ) / np.sqrt( n )
    return mean,sem,n

def line( x, y, e=None, line_color='#000000', line_width=1, sem_color=None, shaded=False, label=None ):
    if e is not None:
        if shaded:
            if sem_color is None:
                sem_color = line_color
            plt.fill_between( x, y-e, y+e, facecolor=sem_color, alpha=0.4, linewidth=0 )
        else:
            if sem_color is None:
                sem_color = '#000000'
            for xx,yy,ee in zip(x,y,e):
                plt.plot( [xx,xx], [yy-ee,yy+ee], color=sem_color, linewidth=1 )
                plt.plot( [xx-0.2,xx+0.2], [yy-ee,yy-ee], color=sem_color, linewidth=1 )
                plt.plot( [xx-0.2,xx+0.2], [yy+ee,yy+ee], color=sem_color, linewidth=1 )
    if label is None:
        plt.plot( x, y, color=line_color, linewidth=line_width )
    else:
        plt.plot( x, y, color=line_color, linewidth=line_width, label=label )

def eye_tracking_parameters( dlcdata ):
    """ Calculate eye tracking parameters """
    # Get the main index name and other summary data
    dlcscorer = dlcdata.columns[0][0]
    n_frames = dlcdata.shape[0]

    # Get x and y coords of pupil center
    pupil_names = ["pupil_left", "pupil_LT", "pupil_top", "pupil_RT", "pupil_right", "pupil_RB", "pupil_bottom", "pupil_LB"]
    pupil_coords_x = np.zeros((n_frames,len(pupil_names)))
    pupil_coords_y = np.zeros((n_frames,len(pupil_names)))
    for point_nr, point_name in enumerate(pupil_names):
        pupil_coords_x[:,point_nr] = dlcdata[dlcscorer,point_name,"x"]
        pupil_coords_y[:,point_nr] = dlcdata[dlcscorer,point_name,"y"]

    # Get eye left coordinates
    eye_left_x = np.array(dlcdata[dlcscorer,"eye_left","x"])
    eye_left_y = np.array(dlcdata[dlcscorer,"eye_left","y"])

    # calculate pupil center
    pupil_center_x = np.mean(pupil_coords_x,axis=1)
    pupil_center_y = np.mean(pupil_coords_y,axis=1)

    # calculate pupil diameter
    n_opps = int(len(pupil_names)/4)
    pupil_diameter = np.zeros((n_frames,n_opps))
    for p_nr in range(n_opps):
        pupil_diameter[:,p_nr] = np.sqrt( np.add( np.square( np.subtract(pupil_coords_x[:,p_nr],pupil_coords_x[:,p_nr+n_opps]) ) , np.square( np.subtract(pupil_coords_y[:,p_nr],pupil_coords_y[:,p_nr+n_opps]) ) ) )
    pupil_diameter = np.mean(pupil_diameter,axis=1)

    # calculate distance from eye left to pupil center
    pupil_shift_x = pupil_center_x-eye_left_x
    pupil_shift_y = pupil_center_y-eye_left_y

    return pupil_shift_x, pupil_shift_y, pupil_diameter

#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# Code

# Load Aux data
auxfilestem = "*"+filestem+"*.lvd"
Aux = auxrec.LvdAuxRecorder(args.filepath, filename=auxfilestem, nimagingplanes=n_imaging_planes)
print(Aux)

# Find visual stimulus onsets in aux data
stim_onsets = Aux.stimulus_onsets

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


# Find matching deeplabcut data
dlcfilestem = "*"+filestem+"*-"+datatype+"DLC*.h5"
dlc_h5_file = glob.glob(os.path.join(args.filepath,dlcfilestem))
do_dlc = False
if len(dlc_h5_file) > 0:
    dlcdata = pd.read_hdf(dlc_h5_file[0])
    do_dlc = True

if "eye" in datatype and do_dlc:
    plot_names = ["Pupil x position","Pupil y position","Pupil diameter"]
    plot_data = eye_tracking_parameters( dlcdata )
    fig,ax = init_figure_axes(fig_size=(8*len(plot_names),8))
    x_range = np.arange(-5,20)
    x_values = x_range / Aux.imagingsf
    for plt_cnt,(name,data) in enumerate(zip(plot_names,plot_data)):
        ax = plt.subplot2grid( (1,len(plot_names)), (0,plt_cnt) )
        data_mat = np.zeros((len(stim_onsets),len(x_range)))
        for tr_nr,tr in enumerate(stim_onsets):
            frames = tr+x_range
            data_mat[tr_nr,:] = data[sync_ixs[frames]]
            plt.plot(x_values,data_mat[tr_nr,:],color="#aaaaaa")
        mn,sem,n = mean_sem( data_mat, axis=0 )
        line( x_values, mn, sem, line_color="#000000", sem_color="#000000" )
        finish_panel( ax, ylabel=name, xlabel="Time (s)", legend="off", x_minmax=[x_values[0],x_values[-1]], x_margin=0.55, x_axis_margin=0.55, despine=True )
    finish_figure( filename=os.path.join("/Users/pgoltstein/figures",filestem+"-example-"+datatype+"-dlc"), wspace=0.6, hspace=0.2 )


#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# show 10 frames around stimulus onset for the 10 first trials

# use_trials = np.arange(1,100,10).astype(int)
# use_frames = np.arange(-1,11).astype(int)
# n_frames_to_load = len(use_trials)*len(use_frames)
# fig,ax = init_figure_axes(fig_size=(len(use_frames)*2,len(use_trials)*1.8))
# with tqdm(total=n_frames_to_load, desc="Reading/processing", unit="Fr") as bar:
#     for tr_cnt,tr in enumerate(use_trials):
#         for fr_cnt,fr in enumerate(use_frames):
#             ax = plt.subplot2grid( (len(use_trials),len(use_frames)), (tr_cnt,fr_cnt) )
#             imaging_frame = stim_onsets[tr]+fr
#             video_frame = sync_ixs[imaging_frame]
#             image = Video[video_frame][:,:,0]
#             plt.imshow(image, cmap='gray', vmin=0, vmax=255)
#             plt.axis('off')
#             if fr_cnt == 0:
#                 plt.title("Trial {}".format(tr), fontsize=8)
#             if fr_cnt == 2:
#                 plt.title("on ->", fontsize=8)
#             bar.update(1)
# finish_figure( filename=os.path.join("/Users/pgoltstein/figures",filestem+"-example-"+datatype+"-sync"), wspace=0.1, hspace=0.4 )


#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# That's all folks!
plt.show()
