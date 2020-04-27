#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

This script tests the module auxrecorder.

Created on Sunday April 12, 2020

@author: pgoltstein
"""

import os, glob
import matplotlib.pyplot as plt
import auxrec
import argparse


# =============================================================================
# Arguments

parser = argparse.ArgumentParser( description = "This script tests the module auxrecorder.\n (written by Pieter Goltstein - April 2020)")
parser.add_argument('filepath', type=str, help= 'path to the folder holding the aux files')
args = parser.parse_args()


# =============================================================================
# Code


print("\nTesting auxrecorder:")
Aux = auxrec.LvdAuxRecorder(args.filepath)
fo,ifi = Aux._calculate_imaging_frames()

print("---- class properties ----")
print("Aux.imagingifi: {} s".format(Aux.imagingifi))
print("Aux.imagingsf: {} Hz".format(Aux.imagingsf))
print("Aux.darkframes: {}".format(Aux.darkframes))
print("Aux.dataonsetframe: {}".format(Aux.dataonsetframe))

# Display channel
plotrange = [0,100000]
plt.subplot(111)
plt.plot(Aux.raw_channel(nr=7)[plotrange[0]:plotrange[1]])
plt.plot(Aux._clean_channel("task", 0.4, 0.5)[plotrange[0]:plotrange[1]])
plt.plot(Aux.raw_channel(nr=3)[plotrange[0]:plotrange[1]])
for f in fo:
    plt.plot(f,1,'or')
    if f > 100000:
        break
plt.show()


print("\nDone testing\n")
