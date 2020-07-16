#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

This script tests the module matlabstimulus.

Created on Thursday 16 July 2020

@author: pgoltstein
"""

import os, glob
import matplotlib.pyplot as plt
import matlabstimulus
import argparse


# =============================================================================
# Arguments

parser = argparse.ArgumentParser( description = "This script tests the module matlabstimulus.\n (written by Pieter Goltstein - July 2020)")
parser.add_argument('filepath', type=str, help= 'path to the folder holding the Matlab stimulus file')
args = parser.parse_args()


# =============================================================================
# Code


print("\nTesting matlabstimulus:")
Stim = matlabstimulus.StimulusData(args.filepath)
print(Stim)

print("\nDone testing\n")
