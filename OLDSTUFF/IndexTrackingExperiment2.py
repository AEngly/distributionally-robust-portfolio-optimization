# ------------ Dependencies ------------

import re
import datetime as dt
import numpy as np
import pandas as pd
from mosek.fusion import *
import re
import math
import time

# -------- MODEL PARAMETERS ---------

rho = 0.30
beta = 0.80
epsCollection = 10**np.linspace(-3, 0, 20)
epsCollection = np.concatenate(([0], epsCollection), axis=0)
totalEps = len(epsCollection)
excessReturnAnually = 0.02
alpha = (1 + excessReturnAnually)**(1/252)-1
rf = 0.0

# -------- EXPERIMENT PARAMETERS ---------

#trainingSizes = np.array(10**np.linspace(1,3,4), dtype=np.int32)     # Check sensitivity to choice of training data size N
trainingSizes = np.array(21*np.linspace(2,18,8), dtype=np.int32)      # Check sensitivity to choice of training data size N
testSize = 126                                                        # Test on 6 months of data (2 quarter)
validationFraction = 0.20                                             # Use 10% data to find the optimal Wasserstein radius
nSimulations = 200                                                    # Fix number of evaluations rather than slideSize
nModels = 2

# ------------ EITP Modules ------------

# Import new models
from EITP.Models.TrackingModelSAA import TrackingModelSAA as TrackingModelSAA;
from EITP.Models.TrackingModelDRO import TrackingModelDRO as TrackingModelDRO;

# Import statistics packages
from EITP.Backtesting.VisualComparison import Visualizer;
from EITP.Backtesting.QuantitativeComparison import PerformanceMetrics;
from EITP.PerformanceEvaluation.QuantitativeStatistics import PerformanceMetrics;

# ------------ Data Imports ------------

historicalConstituents = pd.read_csv("./Data/SP500/HistoricalConstituents.csv");
dailySP500 = pd.read_csv("./Data/SP500/DailyHistoricalPrices.csv");
weeklySP500 = pd.read_csv("./Data/SP500/WeeklyHistoricalPrices.csv");

# Period 1
startDate1 = "1999-01-01"
endDate1 = "2012-01-01"

# Period 2
startDate2 = "2012-01-01"
endDate2 = dt.datetime.today().strftime("%Y-%m-%d")

# All periods
startDate3 = "1999-01-01"
endDate3 = dt.datetime.today().strftime("%Y-%m-%d")

# Period 1
periodOneConstituents = historicalConstituents[historicalConstituents['Date'] >= startDate1]
periodOneConstituents = periodOneConstituents[periodOneConstituents['Date'] < endDate1]

# Period 2
periodTwoConstituents = historicalConstituents[historicalConstituents['Date'] >= startDate2]
periodTwoConstituents = periodTwoConstituents[periodTwoConstituents['Date'] < endDate2]

# Period 3
allConstituents = historicalConstituents[historicalConstituents['Date'] >= startDate3]
allConstituents = allConstituents[allConstituents['Date'] < endDate3]

# Find intersection
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

# Clean

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

# Select dataset
data = dailySP500PeriodTwo

# All dates
dates = data.iloc[:,0]

# Index
index = data.iloc[:,1]
indexReturns = data.iloc[:,1].pct_change().dropna(axis=0).values

# Assets
assets = data.iloc[:,2:]
assetsReturns = data.iloc[:,2:].pct_change().dropna(axis=0).values

# Compute total available scenarios
totalScenarios = indexReturns.shape[0]

# ------------ START EXPERIMENT ------------

columns =    ['WassersteinRadius',
             'Objective',
             'DownsideSemiStandardDeviation',
             'RMSE',
             'MAD',
             'VaR-{}'.format(beta),
             'CVaR-{}'.format(beta),
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

Certificate = np.zeros((nModels, len(trainingSizes), nSimulations))
J = np.zeros((nModels, len(trainingSizes), nSimulations))
epsOpt = np.zeros((len(trainingSizes), nSimulations))

# -------- START ROLLING-WINDOW --------

maxIter = len(trainingSizes)*nSimulations

print("\nStarting Experiment 2:\n")

for h, trainingSize in enumerate(trainingSizes):

    validationSize = math.floor(trainingSize*validationFraction)
    trainingSize = trainingSize - validationSize
    windowSize = trainingSize + validationSize + testSize
    rollingMax = totalScenarios - windowSize
    slideSize = int(rollingMax/nSimulations)
    increments = np.arange(0,rollingMax, slideSize)[:nSimulations]
    totalIncrements = len(increments)

    for i, shift in enumerate(increments):

        # Print progress
        print("Iteration: {}/{}".format(h*nSimulations + i, maxIter))

        # Set displacements based on shift
        startIndex = shift
        endIndex = shift+windowSize-validationSize-testSize
        startIndexValidation = shift + trainingSize
        endIndexValidation = shift + trainingSize + validationSize
        startIndexTesting = shift + trainingSize + validationSize
        endIndexTesting = shift + trainingSize + validationSize + testSize

        # Train model
        MODEL = TrackingModelDRO(returnsAssets=assetsReturns[startIndex:endIndex,:], returnsIndex=indexReturns[startIndex:endIndex], beta=beta, rho=rho, alpha=alpha, rf=rf);
        results = MODEL.solve(epsCollection=epsCollection, progressBar=False);

        # Create aray to find optimal radius
        candidates = np.zeros(totalEps-1)

        # Use validation set to obtain validation performance
        for j in range(1,totalEps):

            # Set weights
            wDRO = np.array(results.iloc[j,6:].values, dtype=np.float64)

            # Set optimal portfolio
            MODEL.setOptimalPortfolio(wDRO)

            # Compute certificate and J
            candidates[j-1] = MODEL.approximateObjective(assetsReturns[startIndexValidation:endIndexValidation,:],
                                                        indexReturns[startIndexValidation:endIndexValidation], wDRO)

        # Get optimal radius
        indexEpsOpt = np.argmin(candidates)
        epsOpt[h,i] = epsCollection[indexEpsOpt+1]

        # Set portfolio
        wOptSAA = np.array(results.iloc[0,6:].values, dtype=np.float64)
        wOptDRO = np.array(results.iloc[indexEpsOpt+1,6:].values, dtype=np.float64)

        # Save in-sample performance
        Certificate[0,h,i] = results.iloc[0,0]
        Certificate[1,h,i] = results.iloc[indexEpsOpt+1,0]

        # Approximate out-of-sample performance
        J[0,h,i] = MODEL.approximateObjective(assetsReturns[startIndexTesting:endIndexTesting,:],
                                                        indexReturns[startIndexTesting:endIndexTesting], wOptSAA)
        J[1,h,i] = MODEL.approximateObjective(assetsReturns[startIndexTesting:endIndexTesting,:],
                                                        indexReturns[startIndexTesting:endIndexTesting], wOptDRO)

# Experiment completed
print("Iteration: {}/{}".format(h*nSimulations + (i+1), maxIter))
print("\nStatus: Completed!\n")

# Save results
a,b,c = Certificate.shape
np.savetxt("./Results/Experiment2_TrackerModelDRO_Certificate_recover_{}_{}_{}.csv".format(a,b,c),
           Certificate.reshape(-1), fmt='%.18e', delimiter=' ')

a,b,c = J.shape
np.savetxt("./Results/Experiment2_TrackerModelDRO_J_recover_{}_{}_{}.csv".format(a,b,c),
           J.reshape(-1), fmt='%.18e', delimiter=' ')

a,b = epsOpt.shape
np.savetxt("./Results/Experiment2_TrackerModelDRO_epsOpt_recover_{}_{}.csv".format(a,b),
           epsOpt.reshape(-1), fmt='%.18e', delimiter=' ')