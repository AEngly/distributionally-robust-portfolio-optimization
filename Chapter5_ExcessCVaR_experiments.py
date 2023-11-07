"""
Author: Andreas Heidelbach Engly (s170303)
Purpose: This file generates the results for chapter 5 of the thesis.

Inputs:
- In order to get the right results, the model parameters must be modified.

Outputs:
- The results are saved into .csv-files.

"""

# Load dependencies
import datetime as dt
import numpy as np
import pandas as pd
from mosek.fusion import *
from tqdm import tqdm
import scipy.stats as sps
import math
import time
import gc

# Imports from module
from EITP.Models.TrackingModelSAA import TrackingModelSAA as TrackingModelSAA;
from EITP.Models.ExcessCVaRModelSAA import ExcessCVaRModelSAA as ExcessCVaRModelSAA;
from EITP.Models.TrackingModelDRO import TrackingModelDRO as TrackingModelDRO;
from EITP.Models.ExcessCVaRModelDRO import ExcessCVaRModelDRO as ExcessCVaRModelDRO;
from EITP.Backtesting.VisualComparison import Visualizer;
from EITP.Backtesting.QuantitativeComparison import PerformanceMetrics;
from EITP.PerformanceEvaluation.QuantitativeStatistics import PerformanceMetrics;
from EITP.Data.DataLoader import DataLoader;

# Print that script is starting
print("\n#########################################################################################\n")
print("                           Reproducing Results for Chapter 5                                 ")
print("\n#########################################################################################\n")

#########################################################################################
#                             Loading Market Data
#########################################################################################

# Start by instantiating the data loader
dataLoader = DataLoader(path='./Data/');
priceData = dataLoader.SP500(freq="daily", startDate="2012-01-01", endDate=dt.datetime.today().strftime("%Y-%m-%d"));
totalObservations = priceData.shape[0]

# Format the output
dates = priceData.iloc[:,0]
index = priceData.iloc[:,1]
indexReturns = priceData.iloc[:,1].pct_change().dropna(axis=0).values
assets = priceData.iloc[:,2:]
assetsReturns = priceData.iloc[:,2:].pct_change().dropna(axis=0).values

# Then we can free priceData from the memory
del priceData
gc.collect()

#########################################################################################
#                             Control Experiments
#########################################################################################

# Specify whether to run experiments or not
runTests = False
runExperiment1 = False
runExperiment2 = True

# Specify number of simulations in each iteration of all experiments
nSimulations = 200

# Specify central parameters
rho = 2
beta = 0.95
excessReturnAnually = 0.0511
rfAnnualy = 0.02

#########################################################################################
#                             Test Runs on Both Models
#########################################################################################

if runTests:

    # Set model parameters
    epsCollection = 10**np.linspace(-4, 0.5, 30)
    totalEps = len(epsCollection)
    alphaDaily = (1 + excessReturnAnually)**(1/252)-1
    rfDaily = (1 + rfAnnualy)**(1/252)-1

    # Run a simple test
    startIndex = 500
    endIndex = startIndex + 700
    print("\nTesting SAA:\n")
    modelSAA = ExcessCVaRModelSAA(returnsAssets=assetsReturns[startIndex:endIndex,:],
                                returnsIndex=indexReturns[startIndex:endIndex],
                                beta=beta,
                                rho=rho,
                                alpha=alphaDaily,
                                rf=rfDaily)
    resultsSAA = modelSAA.solve(rhoCollection=np.array([rho]),
                betaCollection=np.array([beta]), progressBar=True)
    print(resultsSAA)
    print("\nTesting DRO:\n")
    modelDRO = ExcessCVaRModelDRO(returnsAssets=assetsReturns[startIndex:endIndex,:],
                                returnsIndex=indexReturns[startIndex:endIndex],
                                beta=beta,
                                rho=rho,
                                alpha=alphaDaily,
                                rf=rfDaily)
    resultsDRO = modelDRO.solve(epsCollection=np.array([0,10**(-3), 10**(-1)]), rhoCollection=np.array([rho]),
                betaCollection=np.array([beta]), progressBar=True)
    print(resultsDRO)

#########################################################################################
#                Experiment 1 (Sensitivity to Wasserstein Radius)
#########################################################################################

if runExperiment1:

    print("\nRunning Experiment 1:\n")

    # -------- MODEL ----------

    alphaDaily = (1 + excessReturnAnually)**(1/252)-1
    rfDaily = (1 + rfAnnualy)**(1/252)-1
    epsCollection = 10**np.linspace(-4, 0.5, 30)
    epsCollection = np.concatenate(([0], epsCollection), axis=0)
    totalEps = len(epsCollection)
    rhoCollection=np.array([rho])
    betaCollection=np.array([beta])

    # -------- ADJUSTABLE ---------

    #trainingSizes = [126, 189, 252, 378, 504]
    trainingSizes = [126]                           # Train on 6 and 9 months of data (2 and 3 quarter)
    testSize = 126                                  # Test on 6 months of data (2 quarter)

    # -------- PREPARE DATA COLLECTION --------

    columns =    ['WassersteinRadius',
                'Objective',
                'DownsideSemiStandardDeviation',
                'RMSE',
                'MAD',
                'VaR-{}'.format(betaCollection[0]),
                'CVaR-{}'.format(betaCollection[0]),
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

    IS_statistics = np.zeros((len(trainingSizes), nSimulations, len(epsCollection), len(columns)-1))
    OoS_statistics = np.zeros((len(trainingSizes), nSimulations, len(epsCollection), len(columns)-1))
    Weights_vs_Wasserstein = np.zeros((len(trainingSizes), len(epsCollection), assetsReturns.shape[1]+1))

    # -------- START ROLLING-WINDOW --------

    # Initialize progress bar (tqdm causes sempahore leaks, so it is disabled)
    currentIter = 0
    maxIter = nSimulations*len(trainingSizes)
    iterPerSecond = 0
    secPerIter = 0
    timeElapsed = 0
    timeRemaining = 0
    start = time.time()

    # Start the actual experiment
    for h, trainingSize in enumerate(trainingSizes):

        windowSize = trainingSize + testSize
        rollingMax = totalObservations - windowSize
        slideSize = int(rollingMax/nSimulations)
        increments = np.arange(0,rollingMax, slideSize)[:nSimulations]
        totalIncrements = len(increments)

        for i, shift in enumerate(increments):

            # Shift the rolling window
            startIndex = shift
            endIndex = shift+windowSize-testSize

            # Instantiate the model
            MODEL = ExcessCVaRModelDRO(returnsAssets=assetsReturns[startIndex:endIndex,:],
                            returnsIndex=indexReturns[startIndex:endIndex],
                            beta=beta,
                            rho=rho,
                            alpha=alphaDaily,
                            rf=rfDaily)

            # Solve it for all epsilon
            results = MODEL.solve(epsCollection=epsCollection, rhoCollection=rhoCollection,
                                    betaCollection=betaCollection, progressBar=False);

            for j in range(totalEps):

                # Set weights
                w = np.array(results.iloc[j,7:].values, dtype=np.float64)

                # Save weights
                Weights_vs_Wasserstein[h,j,:] += w

                # Set optimal portfolio
                MODEL.setOptimalPortfolio(w)

                # Test in-sample
                assetsPathsIS, indexIS, enhancedIndexIS, portfolioIS = MODEL.IS(plot=False, dataName="S&P500")

                # Test out-of-sample
                assetsPathsOoS, indexOoS, enhancedIndexOoS, portfolioOoS = MODEL.OoS(assetsReturns[windowSize-testSize:windowSize,:],
                                                                                        indexReturns[windowSize-testSize:windowSize], plot=False,
                                                                                        dataName="S&P500")

                # Compute metrics for the first run
                PM_IS = PerformanceMetrics(portfolioIS, indexIS, enhancedIndexIS)
                PM_OoS = PerformanceMetrics(portfolioOoS, indexOoS, enhancedIndexOoS)
                metricsRecordings_IS = PM_IS.getMetrics(rho=rho, beta=beta)
                metricsRecordings_OoS = PM_OoS.getMetrics(rho=rho, beta=beta)
                metricsRecordings_IS['Objective'] = results.iloc[j,0]
                metricsRecordings_OoS['Objective'] = MODEL.approximateObjective(assetsReturns[windowSize-testSize:windowSize,:], indexReturns[windowSize-testSize:windowSize], w)

                # Prepare storage of all performance metrics
                for k, key in enumerate(metricsRecordings_IS):
                    IS_statistics[h,i,j,k] = metricsRecordings_IS[key]
                    OoS_statistics[h,i,j,k] = metricsRecordings_OoS[key]

            # Update progress bar
            currentIter += 1
            end = time.time()
            secPerIter = round(end - start, 2)
            iterPerSecond = 1/secPerIter
            timeElapsed += round(secPerIter, 2)
            timeElapsedMinutes = math.floor(timeElapsed/60)
            timeElapsedSeconds = math.floor(timeElapsed - timeElapsedMinutes*60)
            timeRemaining = (maxIter - currentIter)/iterPerSecond
            timeRemainingMinutes = math.floor(timeRemaining/60)
            timeRemainingSeconds = math.floor(timeRemaining - timeRemainingMinutes*60)

            # Print the progress bar
            if currentIter % 10 == 0 and iterPerSecond > 1:
                print("Activity: Experiment 1 | {}/{} [{}:{}<{}:{}, {}it/s]".format(currentIter, maxIter, str(timeElapsedMinutes).zfill(2), str(timeElapsedSeconds).zfill(2), str(timeRemainingMinutes).zfill(2), str(timeRemainingSeconds).zfill(2), iterPerSecond))
            if currentIter % 10 == 0 and iterPerSecond <= 1:
                print("Activity: Experiment 1 | {}/{} [{}:{}<{}:{}, {}s/it]".format(currentIter, maxIter, str(timeElapsedMinutes).zfill(2), str(timeElapsedSeconds).zfill(2), str(timeRemainingMinutes).zfill(2), str(timeRemainingSeconds).zfill(2), secPerIter))

            # Restart timer
            start = time.time()

    # Save training sizes as list for recovery
    aux = "_".join(str(e) for e in trainingSizes)

    # ------- Save for Wasserstein vs Weights -------
    np.savetxt("./Results/Chapter5_ExcessCVaR/ExcessModelDRO_WassersteinWeights_T_{}_P_{}_{}_S_{}_recover_{}_{}_{}.csv".format(aux,
                                                                                betaCollection[0],
                                                                                rhoCollection[0],
                                                                                nSimulations,
                                                                                len(trainingSizes),
                                                                                len(epsCollection),
                                                                                assetsReturns.shape[1]+1), Weights_vs_Wasserstein.reshape(-1), fmt='%.18e', delimiter=' ')

    # ------- Save all results -------
    a,b,c,d = IS_statistics.shape
    np.savetxt("./Results/Chapter5_ExcessCVaR/Chapter5_Experiment1_ExcessModelDRO_IS_statistics_T_{}_P_{}_{}_S_{}_recover_{}_{}_{}_{}.csv".format(aux,
                                                                                                        beta,
                                                                                                        rho,
                                                                                                        nSimulations,
                                                                                                        a, b, c, d), IS_statistics.reshape(-1), fmt='%.18e', delimiter=' ')
    np.savetxt("./Results/Chapter5_ExcessCVaR/Chapter5_Experiment1_ExcessModelDRO_OoS_statistics_T_{}_P_{}_{}_S_{}_recover_{}_{}_{}_{}.csv".format(aux,
                                                                                                        beta,
                                                                                                        rho,
                                                                                                        nSimulations,
                                                                                                        a, b, c, d), OoS_statistics.reshape(-1), fmt='%.18e', delimiter=' ')

    # -------- Set reference counters to 0 and force garbage collection -------- #
    del IS_statistics
    del OoS_statistics
    del Weights_vs_Wasserstein
    gc.collect()

#########################################################################################
#                Experiment 2 (Sensitivity to Choice of Historical Samples)
#########################################################################################

if runExperiment2:

    print("\nRunning Experiment 2:\n")

    # -------- MODEL PARAMETERS ---------

    # Adjustable
    epsCollection = 10**np.linspace(-3, 0, 20)
    epsCollection = np.concatenate(([0], epsCollection), axis=0)

    # Conversions (should not be modified)
    totalEps = len(epsCollection)
    rhoCollection=np.array([rho])
    betaCollection=np.array([beta])
    alpha = (1 + excessReturnAnually)**(1/252)-1
    rf = (1 + rfAnnualy)**(1/252)-1

    # -------- ADJUSTABLE ---------

    trainingSizes = np.linspace(252,252*2,5, dtype=np.int16)              # Check sensitivity to choice of training data size N
    trainingSizes = np.array([252, 504])
    testSize = 126                                                        # Test on 6 months of data (2 quarter)
    validationFraction = 0.20                                             # Use 10% data to find the optimal Wasserstein radius
    nModels = 2                                                           # We compare SAA and DRO

    # -------- PREPARE DATA COLLECTION --------

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

    # Initialize progress bar (tqdm causes sempahore leaks, so it is disabled)
    currentIter = 0
    maxIter = nSimulations*len(trainingSizes)
    iterPerSecond = 0
    secPerIter = 0
    timeElapsed = 0
    timeRemaining = 0
    start = time.time()

    # Start actual experiment
    for h, trainingSize in enumerate(trainingSizes):

        validationSize = math.floor(trainingSize*validationFraction)
        trainingSize = trainingSize - validationSize
        windowSize = trainingSize + validationSize + testSize
        rollingMax = totalObservations - windowSize
        slideSize = int(rollingMax/nSimulations)
        increments = np.arange(0,rollingMax, slideSize)[:nSimulations]
        totalIncrements = len(increments)

        for i, shift in enumerate(increments):

            # Control moving window
            startIndex = shift
            endIndex = shift+windowSize-validationSize-testSize
            startIndexValidation = shift + trainingSize
            endIndexValidation = shift + trainingSize + validationSize
            startIndexTesting = shift + trainingSize + validationSize
            endIndexTesting = shift + trainingSize + validationSize + testSize

            # Train model
            MODEL = ExcessCVaRModelDRO(returnsAssets=assetsReturns[startIndex:endIndex,:], returnsIndex=indexReturns[startIndex:endIndex], beta=beta, rho=rho, alpha=alpha, rf=rf);

            # Solve it for all epsilon
            results = MODEL.solve(epsCollection=epsCollection, rhoCollection=rhoCollection,
                                    betaCollection=betaCollection, progressBar=False);

            # Create aray to find optimal radius
            candidates = np.zeros(totalEps-1)

            # Use validation set to obtain validation performance
            for j in range(1,totalEps):

                # Set weights
                wDRO = np.array(results.iloc[j,7:].values, dtype=np.float64)

                # Set optimal portfolio
                MODEL.setOptimalPortfolio(wDRO)

                # Compute certificate and J
                candidates[j-1] = MODEL.approximateObjective(assetsReturns[startIndexValidation:endIndexValidation,:],
                                                            indexReturns[startIndexValidation:endIndexValidation], wDRO)

            # Get optimal radius
            indexEpsOpt = np.argmin(candidates)
            epsOpt[h,i] = epsCollection[indexEpsOpt+1]

            # Set portfolio
            wOptSAA = np.array(results.iloc[0,7:].values, dtype=np.float64)
            wOptDRO = np.array(results.iloc[indexEpsOpt+1,7:].values, dtype=np.float64)

            # Save in-sample performance
            Certificate[0,h,i] = results.iloc[0,0]
            Certificate[1,h,i] = results.iloc[indexEpsOpt+1,0]

            # Approximate out-of-sample performance
            J[0,h,i] = MODEL.approximateObjective(assetsReturns[startIndexTesting:endIndexTesting,:],
                                                            indexReturns[startIndexTesting:endIndexTesting], wOptSAA)
            J[1,h,i] = MODEL.approximateObjective(assetsReturns[startIndexTesting:endIndexTesting,:],
                                                            indexReturns[startIndexTesting:endIndexTesting], wOptDRO)

            # Update progress bar
            currentIter += 1
            end = time.time()
            secPerIter = round(end - start, 2)
            iterPerSecond = round(1/secPerIter, 2)
            timeElapsed += round(secPerIter, 2)
            timeElapsedMinutes = math.floor(timeElapsed/60)
            timeElapsedSeconds = math.floor(timeElapsed - timeElapsedMinutes*60)
            timeRemaining = (maxIter - currentIter)/iterPerSecond
            timeRemainingMinutes = math.floor(timeRemaining/60)
            timeRemainingSeconds = math.floor(timeRemaining - timeRemainingMinutes*60)

            # Print the progress bar
            if currentIter % 10 == 0 and iterPerSecond > 1:
                print("Activity: Experiment 2 | {}/{} [{}:{}<{}:{}, {}it/s]".format(currentIter, maxIter, str(timeElapsedMinutes).zfill(2), str(timeElapsedSeconds).zfill(2), str(timeRemainingMinutes).zfill(2), str(timeRemainingSeconds).zfill(2), iterPerSecond))
            if currentIter % 10 == 0 and iterPerSecond <= 1:
                print("Activity: Experiment 2 | {}/{} [{}:{}<{}:{}, {}s/it]".format(currentIter, maxIter, str(timeElapsedMinutes).zfill(2), str(timeElapsedSeconds).zfill(2), str(timeRemainingMinutes).zfill(2), str(timeRemainingSeconds).zfill(2), secPerIter))

            # Restart timer
            start = time.time()

    # Save results
    a,b,c = Certificate.shape
    np.savetxt("./Results/Chapter5_ExcessCVaR/Chapter5_Experiment2_ExcessModelDRO_Certificate_recover_{}_{}_{}.csv".format(a,b,c),
            Certificate.reshape(-1), fmt='%.18e', delimiter=' ')

    a,b,c = J.shape
    np.savetxt("./Results/Chapter5_ExcessCVaR/Chapter5_Experiment2_ExcessModelDRO_J_recover_{}_{}_{}.csv".format(a,b,c),
            J.reshape(-1), fmt='%.18e', delimiter=' ')

    a,b = epsOpt.shape
    np.savetxt("./Results/Chapter5_ExcessCVaR/Chapter5_Experiment2_ExcessModelDRO_epsOpt_recover_{}_{}.csv".format(a,b),
            epsOpt.reshape(-1), fmt='%.18e', delimiter=' ')