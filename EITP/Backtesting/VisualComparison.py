import sys
import os
import re
import glob
import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from mosek.fusion import *
from tqdm import tqdm
import scipy.stats as sps

class Visualizer:

    def __init__(self, portfolios, assetsOoS, indexOoS, enhancedIndexOoS, alphaAnnualy=0.0510, dataSet='GMS'):

        self.portfolios = portfolios;
        self.assets = assetsOoS;
        self.index = indexOoS;
        self.enhancedIndex = enhancedIndexOoS;
        self.alphaAnnualy = alphaAnnualy;
        self.dataSet = dataSet;

    def compareTracking(self, benchmarkName="Benchmark", fileName=None, maxTerminal=300, opacity=0.3, extended=False, size=(16,16), firstylim=[75,125], ylim=[-15,3], compareModels=['BaseModel', 'BaseModelDRO']):

        if extended:

            fig, ax = plt.subplots(ncols=2, figsize=size)

            ax[0].plot(self.assets[:,self.assets[-1,:] < maxTerminal], alpha = opacity);
            ax[0].plot(self.index, label=r'{} ({})'.format(benchmarkName, self.dataSet, self.alphaAnnualy), linestyle='--', linewidth=3, color = 'black', alpha=1.0)
            ax[0].plot(self.enhancedIndex, label=r'Enhanced {} [$\alpha = {}$] ({})'.format(benchmarkName, self.alphaAnnualy, self.dataSet), linestyle='-.', linewidth=3, color = 'blue', alpha=1.0)

            for key in self.portfolios:
                ax[0].plot(self.portfolios[key], label=r'{} (trained on {})'.format(key, self.dataSet), linestyle='-', linewidth=3, alpha=1.0);

            # Title, labels and grid
            ax[0].set_ylim(bottom=firstylim[0], top=firstylim[1])
            ax[0].set_xlabel("Periods");
            ax[0].set_ylabel("Index (period 0 = 100)");
            ax[0].legend(loc="lower left", fontsize="large");
            indexedP1 = self.portfolios[compareModels[0]][:,0];
            indexedP2 = self.portfolios[compareModels[1]][:,0];
            returnEnhancedIndex1 = np.array([(self.enhancedIndex[i+1]/self.enhancedIndex[i]-1)*100 for i in range(len(self.enhancedIndex)-1)]);
            returnsP1 = np.array([(indexedP1[i+1]/indexedP1[i]-1)*100 for i in range(len(indexedP1)-1)]);
            returnsP2 = np.array([(indexedP2[i+1]/indexedP2[i]-1)*100 for i in range(len(indexedP2)-1)]);

            diff11 = returnsP1 - returnEnhancedIndex1;
            diff12 = returnsP2 - returnEnhancedIndex1;
            diff11Cum = np.cumprod((returnsP1 - returnEnhancedIndex1)/100 + 1);
            diff11Cum = (np.insert(diff11Cum, 0, 1.0, axis=0) - 1) * 100;
            diff12Cum = np.cumprod((returnsP2 - returnEnhancedIndex1)/100 + 1);
            diff12Cum = (np.insert(diff12Cum, 0, 1.0, axis=0) - 1) * 100;
            periods = np.array([i for i in range(1,len(diff11)+1)]);

            ax[1].set_ylabel('Return Errors [%]');
            ax[1].bar(periods-0.2, diff11, color='red', width=0.4, label="Enhanced Index vs. {} [%] (right axis)".format(compareModels[0]));
            ax[1].bar(periods+0.2, diff12, color='black', width=0.4, label="Enhanced Index vs. {} [%] (right axis)".format(compareModels[1]));
            ax[1].plot(diff11Cum, color='red', label="Enhanced Index vs. {} [Cummulative %] (right axis)".format(compareModels[0]));
            ax[1].plot(diff12Cum, color='black', label="Enhanced Index vs. {} [Cummulative %] (right axis)".format(compareModels[1]));
            ax[1].set_ylim(ylim[0],ylim[1]);
            ax[1].legend(loc="lower left", fontsize="large");
            ax[1].set_xlabel("Periods");

            # Grid lines
            ax[0].grid(True, linestyle='-', linewidth=0.3);
            ax[1].grid(True, linestyle='-', linewidth=0.3);

        else:

            # Create figure
            fig, ax = plt.subplots(figsize=size)

            ax.plot(self.assets[:,self.assets[-1,:] < maxTerminal], alpha = opacity);
            ax.plot(self.index, label=r'{} ({})'.format(benchmarkName, self.dataSet, self.alphaAnnualy), linestyle='--', linewidth=3, color = 'black', alpha=1.0)
            ax.plot(self.enhancedIndex, label=r'Enhanced {} [$\alpha = {}$] ({})'.format(benchmarkName, self.alphaAnnualy, self.dataSet), linestyle='-.', linewidth=3, color = 'blue', alpha=1.0)
            ax.set_ylim(bottom=firstylim[0], top=firstylim[1])

            for key in self.portfolios:
                ax.plot(self.portfolios[key], label=r'{} (trained on {})'.format(key, self.dataSet), linestyle='-', linewidth=3, alpha=1.0);

            # Title, labels and grid
            ax.set_xlabel("Periods");
            ax.set_ylabel("Index [period 0 = 100]");
            ax.legend(loc="lower left", fontsize="large");

        # Save results
        if fileName is not None:
            plt.savefig('./Plots/{}.png'.format(fileName), dpi=200);

        # Show plot
        plt.show()

    def compareDistributions(self, P1, P2, fileName="comparisonDistributions"):

        indexedP1 = self.portfolios[P1][:,0];
        indexedP2 = self.portfolios[P2][:,0];

        returnsIndex1 = np.array([(self.index[i+1]/self.index[i]-1)*100 for i in range(len(self.index)-1)]);
        returnEnhancedIndex1 = np.array([(self.enhancedIndex[i+1]/self.enhancedIndex[i]-1)*100 for i in range(len(self.enhancedIndex)-1)]);
        returnsP1 = np.array([(indexedP1[i+1]/indexedP1[i]-1)*100 for i in range(len(indexedP1)-1)]);
        returnsP2 = np.array([(indexedP2[i+1]/indexedP2[i]-1)*100 for i in range(len(indexedP2)-1)]);

        diff11 = returnsP1 - returnEnhancedIndex1;
        diff12 = returnsP2 - returnEnhancedIndex1;

        loc_norm_11_portfolio, scale_norm_11_portfolio = sps.norm.fit(diff11);
        loc_norm_12_portfolio, scale_norm_12_portfolio = sps.norm.fit(diff12);

        plt.figure(figsize=(16,10), dpi=200)
        plt.hist(diff11, bins = 30, density = True, cumulative=True, alpha = 0.5, label="Empirical CDF of {}".format(P1))
        plt.hist(diff12, bins = 30, density = True, cumulative=True, alpha = 0.5, label="Empirical CDF of {}".format(P2))
        plt.plot(np.sort(diff11), sps.norm.cdf(np.sort(diff11), loc=loc_norm_11_portfolio, scale=scale_norm_11_portfolio), color = 'blue', label = 'Normal CDF of {}'.format(P1))
        plt.plot(np.sort(diff12), sps.norm.cdf(np.sort(diff12), loc=loc_norm_12_portfolio, scale=scale_norm_12_portfolio), color = 'orange', label = 'Normal CDF of {}'.format(P2))
        plt.xlabel("Returns [%]")
        plt.ylabel("Frequency")

        # Grid lines
        plt.grid(True, linestyle='-', linewidth=0.3);

        # Plot legend
        plt.legend()

        # Save plot
        if fileName is not None:
            plt.savefig('./Plots/{}.png'.format(fileName), dpi=200);

        # Show plot
        plt.show()

    def resultsTable1():
        print("Here I need to implement a table with relevant metrics");

