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

# plt.subplot(111)
# plt.plot(auxvar)
# plt.show()

print("\nDone testing\n")
