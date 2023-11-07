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

class PerformanceMetrics:

    def __init__(self, portfolio, indexOoS, enhancedIndexOoS):

        self.portfolio = portfolio;
        self.index = indexOoS;
        self.enhancedIndex = enhancedIndexOoS;

        # Compute returns to compare
        self.returnEnhancedIndex = np.array([(self.enhancedIndex[i+1]/self.enhancedIndex[i]-1) for i in range(len(self.enhancedIndex)-1)]);
        self.returnIndex = np.array([(self.index[i+1]/self.index[i]-1) for i in range(len(self.index)-1)]);
        self.returnsPortfolio = np.array([(self.portfolio[i+1]/self.portfolio[i]-1) for i in range(len(self.portfolio)-1)]);

    # METRICS
    def DownsideSemiStandardDeviation(self, returns, target):
        return np.sqrt(np.mean(np.square(np.minimum(returns - target, 0))));

    def UpsideSemiStandardDeviation(self, returns, target):
        return np.sqrt(np.mean(np.square(np.maximum(returns - target, 0))));

    def AverageExcessReturn(self, returns, target):
        return np.mean(returns - target);

    def SortinoIndex(self, returns, target):
        return self.AverageExcessReturn(returns, target) / self.DownsideSemiStandardDeviation(returns, target);

    def BeatBenchmarkRatio(self, returns, target):
        return np.mean(returns > target);

    def TotalReturn(self, portfolio):
        return (portfolio[-1] - 100)[0];

    def TotalExcessReturn(self, portfolio, benchmark):
        return (portfolio[-1] - benchmark[-1])[0];

    def RMSE(self, returns, target):
        return np.sqrt(np.mean(np.square(returns - target)));

    def MAD(self, returns, target):
        return np.mean(np.abs(returns - target));

    def VaR(self, returns, target, beta=0.05):
        return np.percentile(returns-target, (1-beta)*100);

    def CVaR(self, returns, target, beta=0.05):
        e = returns-target
        return -np.mean(e[e <= self.VaR(returns, target, beta=beta)]);

    def AverageReturn(self, returns):
        return np.mean(returns)*100;

    def ExcessReturnAverage(self, returns, target, weekly=True):
        rAvg = self.AverageReturn(returns);
        rIAvg = self.AverageReturn(target);
        return rAvg - rIAvg;

    def Percentile(self, returns, target, pth=10, weekly=True):
        return np.percentile(returns-target, pth);

    # Printing the table of metrics
    def getMetrics(self, objective=None, rho=0.6, beta=0.80, printResult=False):

        result = dict();

        # Compute the metrics for all the returns defined in the constructor
        result['Objective'] = objective;
        result['DownsideSemiStandardDeviation'] = self.DownsideSemiStandardDeviation(self.returnsPortfolio, self.returnEnhancedIndex);
        result['RMSE'] = self.RMSE(self.returnsPortfolio, self.returnEnhancedIndex)
        result['MAD'] = self.MAD(self.returnsPortfolio, self.returnEnhancedIndex)
        result['VaR-{}'.format(beta)] = self.VaR(self.returnsPortfolio, self.returnEnhancedIndex, beta=beta)
        result['CVaR-{}'.format(beta)] = self.CVaR(self.returnsPortfolio, self.returnEnhancedIndex, beta=beta)
        result['ExcessReturnAverage'] = self.ExcessReturnAverage(self.returnsPortfolio, self.returnEnhancedIndex);
        result['ExcessReturn'] = self.TotalExcessReturn(self.portfolio, self.enhancedIndex);
        result['SortinoIndex'] = self.SortinoIndex(self.returnsPortfolio, self.returnEnhancedIndex);
        result['BeatBenchmarkRatio'] = self.BeatBenchmarkRatio(self.returnsPortfolio, self.returnEnhancedIndex);
        result['TotalReturn'] = self.TotalReturn(self.portfolio);
        result['AverageReturn'] = self.AverageReturn(self.returnsPortfolio);
        result['P5'] = self.Percentile(self.returnsPortfolio, self.returnEnhancedIndex, pth=5);
        result['P10'] = self.Percentile(self.returnsPortfolio, self.returnEnhancedIndex, pth=10);
        result['P90'] = self.Percentile(self.returnsPortfolio, self.returnEnhancedIndex, pth=90);
        result['P95'] = self.Percentile(self.returnsPortfolio, self.returnEnhancedIndex, pth=90);

        # Make a nice latex table that can be saved to a file
        if printResult:
            print(pd.DataFrame(result).to_latex(float_format="%.4f"));

        # Return the results
        return result;


