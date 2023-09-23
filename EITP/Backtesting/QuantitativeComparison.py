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

    def __init__(self, portfolios, assetsOoS, indexOoS, enhancedIndexOoS, dataSet='GMS'):

        self.portfolios = portfolios;
        self.assets = assetsOoS;
        self.index = indexOoS;
        self.enhancedIndex = enhancedIndexOoS;
        self.dataSet = dataSet;
        self.models = ['BaseModel', 'BaseModelDRO', 'EWCVaR'];

        # Compute returns to compare
        self.returnEnhancedIndex = np.array([(self.enhancedIndex[i+1]/self.enhancedIndex[i]-1) for i in range(len(self.enhancedIndex)-1)]);
        self.returnIndex = np.array([(self.index[i+1]/self.index[i]-1) for i in range(len(self.index)-1)]);
        self.returnsModels = dict();
        for model in self.models:
            self.returnsModels[model] = np.array([(self.portfolios[model][i+1]/self.portfolios[model][i]-1) for i in range(len(self.portfolios[model])-1)]);
            self.returnsModels[model] = self.returnsModels[model][:,0];
            self.portfolios[model] = self.portfolios[model][:,0];

    # METRICS
    def DownsideSemiStandardDeviation(self, returns, target):
        return np.sqrt(np.mean(np.square(np.minimum(returns - target, 0))))*100;

    def UpsideSemiStandardDeviation(self, returns, target):
        return np.sqrt(np.mean(np.square(np.maximum(returns - target, 0))))*100;

    def AverageExcessReturn(self, returns, target):
        return np.mean(returns - target);

    def SortinoIndex(self, returns, target):
        return self.AverageExcessReturn(returns, target) / self.DownsideSemiStandardDeviation(returns, target);

    def BeatBenchmarkRatio(self, returns, target):
        return np.mean(returns > target)*100;

    def TotalReturn(self, portfolio):
        return portfolio[-1] - 100;

    def TotalExcessReturn(self, portfolio, benchmark):
        return portfolio[-1] - benchmark[-1];

    def RMSE(self, returns, target):
        return np.sqrt(np.mean(np.square(returns - target)))*100;

    def AverageReturn(self, returns, weekly=True):
        if weekly:
            return ((1 + np.mean(returns))**52 - 1)*100;
        else:
            return ((1 + np.mean(returns))**12 - 1)*100;

    def ExcessReturnAverage(self, returns, target, weekly=True):
        rAvg = self.AverageReturn(returns, weekly=weekly);
        rIAvg = self.AverageReturn(target, weekly=weekly);
        return rAvg - rIAvg;

    # Printing the table of metrics
    def printMetrics(self, enhanced=False):

        result = dict();
        result['BaseModel'] = dict();
        result['BaseModelDRO'] = dict();
        result['EWCVaR'] = dict();

        if enhanced:

            for model in self.models:

                # Compute the metrics for all the returns defined in the constructor
                result[model]['DownsideSemiStandardDeviation'] = self.DownsideSemiStandardDeviation(self.returnsModels[model], self.returnEnhancedIndex);
                result[model]['RMSE'] = self.RMSE(self.returnsModels[model], self.returnEnhancedIndex)
                result[model]['ExcessReturnAverage'] = self.ExcessReturnAverage(self.returnsModels[model], self.returnEnhancedIndex);
                result[model]['ExcessReturn'] = self.TotalExcessReturn(self.portfolios[model], self.returnIndex);
                result[model]['SortinoIndex'] = self.SortinoIndex(self.returnsModels[model], self.returnEnhancedIndex);
                result[model]['BeatBenchmarkRatio'] = self.BeatBenchmarkRatio(self.returnsModels[model], self.returnEnhancedIndex);
                result[model]['TotalReturn'] = self.TotalReturn(self.portfolios[model]);
                result[model]['AverageReturn'] = self.AverageReturn(self.returnsModels[model]);

        else:

            for model in self.models:

                # Compute the metrics for all the returns defined in the constructor
                result[model]['DownsideSemiStandardDeviation'] = self.DownsideSemiStandardDeviation(self.returnsModels[model], self.returnIndex);
                result[model]['RMSE'] = self.RMSE(self.returnsModels[model], self.returnIndex);
                result[model]['ExcessReturnAverage'] = self.ExcessReturnAverage(self.returnsModels[model], self.returnIndex);
                result[model]['ExcessReturn'] = self.TotalExcessReturn(self.portfolios[model], self.index);
                result[model]['SortinoIndex'] = self.SortinoIndex(self.returnsModels[model], self.returnIndex);
                result[model]['BeatBenchmarkRatio'] = self.BeatBenchmarkRatio(self.returnsModels[model], self.returnIndex);
                result[model]['TotalReturn'] = self.TotalReturn(self.portfolios[model]);
                result[model]['AverageReturn'] = self.AverageReturn(self.returnsModels[model]);

        # Make a nice latex table that can be saved to a file
        print(pd.DataFrame(result).to_latex(float_format="%.4f"));

        # Return the results
        return result;


