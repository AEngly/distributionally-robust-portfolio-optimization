# Dependencies

import sys
import os
import re
import glob
import datetime as dt
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from mosek.fusion import *
from tqdm import tqdm
import time
import scipy.stats as sps
import re

# --------- Model specifications ---------

# Evaluation parameters
windowSize = 252 # Train on 1 year of data
testSize = 63    # Test on 3 months of data (1 quarter)
slideSize = 252  # Slide the window by 1 year

# Set model parameters
gamma = 0.60
beta = 0.95
epsCollection = np.concatenate((np.array([0]), 10**np.linspace(-6, 1, 30)))
alphaAnnualy = 0.00
shortingCapacity = 0.00

# Import custom modules

from EITP.OldModels.BaseModel import IndexTracker as firstModel;
from EITP.OldModels.Model1DRO import IndexTracker as firstModelDRO;
from EITP.Models.EWCVaR import IndexTracker as EWCVaR;
from EITP.OldModels.ModelDRONew import IndexTracker as ModelDRO;
from EITP.Backtesting.VisualComparison import Visualizer;
from EITP.Backtesting.QuantitativeComparison import PerformanceMetrics;
from EITP.PerformanceEvaluation.QuantitativeStatistics import PerformanceMetrics;

# Data Imports and Preparation
historicalConstituents = pd.read_csv("./Data/SP500/HistoricalConstituents.csv");
dailySP500 = pd.read_csv("./Data/SP500/DailyHistoricalPrices.csv");
weeklySP500 = pd.read_csv("./Data/SP500/WeeklyHistoricalPrices.csv");

# Specify periods to investigate
# Period 1
startDate1 = "1999-01-01"
endDate1 = "2012-01-01"

# Period 2
startDate2 = "2012-01-01"
endDate2 = dt.datetime.today().strftime("%Y-%m-%d")

# All periods
startDate3 = "1999-01-01"
endDate3 = dt.datetime.today().strftime("%Y-%m-%d")

# Construct the datasets
# Period 1
periodOneConstituents = historicalConstituents[historicalConstituents['Date'] >= startDate1]
periodOneConstituents = periodOneConstituents[periodOneConstituents['Date'] < endDate1]

# Period 2
periodTwoConstituents = historicalConstituents[historicalConstituents['Date'] >= startDate2]
periodTwoConstituents = periodTwoConstituents[periodTwoConstituents['Date'] < endDate2]

# Period 3
allConstituents = historicalConstituents[historicalConstituents['Date'] >= startDate3]
allConstituents = allConstituents[allConstituents['Date'] < endDate3]

# Get the tickers
P1 = len(periodOneConstituents['Tickers'])
tickersPeriodOne = set(periodOneConstituents['Tickers'].iloc[0].split(","))
for i in range(1, P1):
    iterativeSetPeriodOne = set(periodOneConstituents['Tickers'].iloc[i].split(","))
    tickersPeriodOne = tickersPeriodOne.intersection(iterativeSetPeriodOne)

P2 = len(periodTwoConstituents['Tickers'])
tickersPeriodTwo = set(periodTwoConstituents['Tickers'].iloc[0].split(","))
for i in range(1, P2):
    iterativeSetPeriodTwo = set(periodTwoConstituents['Tickers'].iloc[i].split(","))
    tickersPeriodTwo = tickersPeriodTwo.intersection(iterativeSetPeriodTwo)

P3 = len(allConstituents['Tickers'])
tickersAll = set(allConstituents['Tickers'].iloc[0].split(","))
for i in range(1, P3):
    iterativeSetAll = set(allConstituents['Tickers'].iloc[i].split(","))
    tickersAll = tickersAll.intersection(iterativeSetAll)

# Adjust tickers
# Period 1
text = " ".join(tickersPeriodOne)
matches = re.findall(r'\b\w+\.\w+\b', text)
replacements = [ticker.replace(".", "-") for ticker in matches]
tickersPeriodOne = tickersPeriodOne.difference(matches)
tickersPeriodOne = tickersPeriodOne.union(replacements)

# Period 2
text = " ".join(tickersPeriodTwo)
matches = re.findall(r'\b\w+\.\w+\b', text)
replacements = [ticker.replace(".", "-") for ticker in matches]
tickersPeriodTwo = tickersPeriodTwo.difference(matches)
tickersPeriodTwo = tickersPeriodTwo.union(replacements)

# Period 3
text = " ".join(tickersAll)
matches = re.findall(r'\b\w+\.\w+\b', text)
replacements = [ticker.replace(".", "-") for ticker in matches]
tickersAll = tickersAll.difference(matches)
tickersAll = tickersAll.union(replacements)

# Segment
# Period 1
dailySP500PeriodOne = dailySP500[dailySP500['Dates'] >= startDate1]
dailySP500PeriodOne = dailySP500PeriodOne[dailySP500PeriodOne['Dates'] < endDate1]

# Period 2
dailySP500PeriodTwo = dailySP500[dailySP500['Dates'] >= startDate2]
dailySP500PeriodTwo = dailySP500PeriodTwo[dailySP500PeriodTwo['Dates'] < endDate2]

# Period 3
dailySP500PeriodThree = dailySP500[dailySP500['Dates'] >= startDate3]
dailySP500PeriodThree = dailySP500PeriodThree[dailySP500PeriodThree['Dates'] < endDate3]

# Select prices
# Period 1
keyErrorTickers = set(['ACE', 'JCP', 'WIN', 'BMC', 'CCE', 'NYX', 'TE', 'GR', 'DF', 'MOLX'])
dailySP500PeriodOne = dailySP500PeriodOne[['Dates', 'SPX-INDEX'] + list(tickersPeriodOne - keyErrorTickers)].dropna(axis=1)

# Period 2
keyErrorTickers = set()
dailySP500PeriodTwo = dailySP500PeriodTwo[['Dates', 'SPX-INDEX'] + list(tickersPeriodTwo - keyErrorTickers)].dropna(axis=1)

# Period 3
keyErrorTickers = set()
dailySP500PeriodThree = dailySP500PeriodThree[['Dates', 'SPX-INDEX'] + list(tickersAll - keyErrorTickers)].dropna(axis=1)

# Select the data to be used in evaluation
data = dailySP500PeriodOne

# Compute returns
# All dates
dates = data.iloc[:,0]

# Index
index = data.iloc[:,1]
indexReturns = data.iloc[:,1].pct_change().dropna(axis=0).values

# Assets
assets = data.iloc[:,2:]
assetsReturns = data.iloc[:,2:].pct_change().dropna(axis=0).values

# Run evaluation

# -------- CONSTANTS ---------

T = indexReturns.shape[0]
rollingMax = T - windowSize
increments = np.arange(0,rollingMax, slideSize)

# -------- PREPARE DATA COLLECTION --------

columns =    ['eps',
             'gamma',
             'beta',
             'delta',
             'Objective',
             'DownsideSemiStandardDeviation',
             'RMSE',
             'ExcessReturnAverage',
             'ExcessReturn',
             'SortinoIndex',
             'BeatBenchmarkRatio',
             'TotalReturn',
             'AverageReturn',
             'P5',
             'P10',
             'P90',
             'P95']

IS_data = np.zeros((len(epsCollection), len(columns)))
OoS_data = np.zeros((len(epsCollection), len(columns)))
IS_statistics = pd.DataFrame(IS_data, columns=columns)
OoS_statistics = pd.DataFrame(OoS_data, columns=columns)

# -------- ROLLING-WINDOW --------

with tqdm(total=len(increments)*len(epsCollection)) as pbar:

    for idx, eps in enumerate(epsCollection):

        # -------- FIRST RUN --------

        # Train model
        startIndex = 0
        endIndex = windowSize-testSize
        MODEL = ModelDRO(returnsAssets=assetsReturns[startIndex:endIndex,:], returnsIndex=indexReturns[startIndex:endIndex], betas=[beta], gammas=[gamma], shortingCapacity=shortingCapacity, alphaAnnualy=alphaAnnualy);
        results = MODEL.solve(epsCollection=[eps], progressBar=False);

        # Test in-sample
        selectedDate, indexIS, enhancedIndexIS, portfolioIS = MODEL.IS(plot=False, dataName="S&P500")

        # Test out-of-sample
        selectedDate, indexOoS, enhancedIndexOoS, portfolioOoS = MODEL.OoS(assetsReturns[windowSize-testSize:windowSize,:], indexReturns[windowSize-testSize:windowSize], plot=False, dataName="S&P500")

        # Compute metrics for the first run
        PM_IS = PerformanceMetrics(portfolioIS, indexIS, enhancedIndexIS)
        PM_OoS = PerformanceMetrics(portfolioOoS, indexOoS, enhancedIndexOoS)
        metricsRecordings_IS = PM_IS.getMetrics()
        metricsRecordings_OoS = PM_OoS.getMetrics()

        # Prepare storage of all performance metrics
        for key in metricsRecordings_IS:
            metricsRecordings_IS[key] = [metricsRecordings_IS[key]]
            metricsRecordings_OoS[key] = [metricsRecordings_OoS[key]]

        # Update progress bar
        pbar.update(1)

        # -------- SUBSEQUENT RUN --------

        for shift in increments[1:]:

            # Train model
            startIndex = shift
            endIndex = shift+windowSize-testSize
            MODEL = ModelDRO(returnsAssets=assetsReturns[startIndex:endIndex,:], returnsIndex=indexReturns[startIndex:endIndex], betas=[beta], gammas=[gamma], shortingCapacity=shortingCapacity, alphaAnnualy=alphaAnnualy);
            results = MODEL.solve(epsCollection=[eps], progressBar=False);

            # Test in-sample
            selectedData, indexIS, enhancedIndexIS, portfolioIS = MODEL.IS(plot=False, dataName="S&P500")

            # Test out-of-sample
            startIndex = shift+windowSize-testSize
            endIndex = shift+windowSize
            selectedData, indexOoS, enhancedIndexOoS, portfolioOoS = MODEL.OoS(assetsReturns[startIndex:endIndex,:], indexReturns[startIndex:endIndex], plot=False, dataName="S&P500")

            # Compute metrics
            PM_IS = PerformanceMetrics(portfolioIS, indexIS, enhancedIndexIS)
            PM_OoS = PerformanceMetrics(portfolioOoS, indexOoS, enhancedIndexOoS)
            results_IS = PM_IS.getMetrics()
            results_OoS = PM_OoS.getMetrics()

            # Store results
            for key in metricsRecordings_IS:
                metricsRecordings_IS[key].append(results_IS[key])
                metricsRecordings_OoS[key].append(results_OoS[key])

            # Update progress bar
            pbar.update(1)

        # Compute average performance
        meanRow_IS = []
        meanRow_OoS = []
        for key in metricsRecordings_IS:
            meanIS = np.mean(metricsRecordings_IS[key])
            meanOoS = np.mean(metricsRecordings_OoS[key])
            meanRow_IS.append(meanIS)
            meanRow_OoS.append(meanOoS)

        # Save the results
        modelSpecifications = list(results.iloc[0,1:5].values)
        IS_statistics.iloc[idx,:] = modelSpecifications + meanRow_IS
        OoS_statistics.iloc[idx,:] = modelSpecifications + meanRow_OoS

# Save the results
IS_statistics.to_csv("./Results/DRO_IS_statistics.csv")
OoS_statistics.to_csv("./Results/DRO_OoS_statistics.csv")