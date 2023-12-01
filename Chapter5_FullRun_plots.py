import numpy as np
import pandas as pd
import os
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

plt.rcParams['text.usetex'] = True
plt.rcParams['mathtext.fontset'] = 'custom'
plt.rcParams['mathtext.rm'] = 'Bitstream Vera Sans'
plt.rcParams['mathtext.it'] = 'Bitstream Vera Sans:italic'
plt.rcParams['mathtext.bf'] = 'Bitstream Vera Sans:bold'
def_font_size = 12
plt.rcParams.update({'font.size': def_font_size})

relativePath = "./Results/Chapter5_FullRun/"
relativePlotPath = "./ResultsPlots/Chapter5_FullRun/"

# PLOT 1: Plot of the different trajectories

# Load data
trajectories = pd.read_csv(relativePath + "fullRunResults.csv", parse_dates=['Dates'])
dates = trajectories['Dates']
trajectories = trajectories.drop(columns=['Dates']).cumprod(axis=0)

# Create plots
fig, ax = plt.subplots(1, 1, figsize=(12, 12))
ax.plot(dates, trajectories.values, label=['Index', 'Enhanced Index', 'SAA', 'DRO'])
ax.set_xlabel('Dates')
ax.set_ylabel(r'Cummulative Wealth [\$]')
plt.legend()
plt.savefig(relativePlotPath + "ExcessCVaRHoldOut.png")
#plt.show()

# PLOT 2: Plot of optimal epsilons

# Load data
epsilons = pd.read_csv(relativePath + "epsOpt.csv", parse_dates=['Dates'])
dates = epsilons['Dates']
epsOpt = epsilons.drop(columns=['Dates'])

# Create plots
fig, ax = plt.subplots(1, 1, figsize=(12, 12))
ax.plot(dates, epsOpt.values, label=['epsOpt'])
ax.set_xlabel('Dates')
ax.set_ylabel(r'Wasserstein Radius [$\epsilon$]')
ax.set_yscale('log')
plt.legend()
plt.savefig(relativePlotPath + "epsOpt.png")
#plt.show()
