"""
Author: Andreas Heidelbach Engly (s170303)
Purpose: This file generates the results for chapter 5 of the thesis.

Inputs:
- In order to get the right results, the model parameters must be modified.

Outputs:
- The results are saved into .csv-files. They are reshaped into 1D-arrays to save space.
- The right dimension are given from the file names.
"""

# Load dependencies
import datetime as dt
import numpy as np
from mosek.fusion import *
from tqdm import tqdm
import time
import re
import math
import gc

# Imports from module
from EITP.Models.TrackingModelSAA import TrackingModelSAA as TrackingModelSAA;
from EITP.Models.TrackingModelDRO import TrackingModelDRO as TrackingModelDRO;
from EITP.PerformanceEvaluation.QuantitativeStatistics import PerformanceMetrics;
from EITP.Data.DataLoader import DataLoader;

# Print that script is starting
print("\n#########################################################################################\n")
print("                           Reproducing Results for Chapter 4                                 ")
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
del dataLoader
del priceData
gc.collect()

#########################################################################################
#                             Control Experiments
#########################################################################################

# Specify whether to run experiments or not
runTests = False
runExperiment1 = True
runExperiment2 = True

# Specify number of simulations in each iteration of all experiments
nSimulations = 200

# Specify central parameters
rho = 0.3
beta = 0.80
excessReturnAnually = 0.0511
rfAnnualy = 0.02

# Don't change these
epsCollection = 10**np.linspace(-4, 0.5, 10)
totalEps = len(epsCollection)
alphaDaily = (1 + excessReturnAnually)**(1/252)-1
rfDaily = (1 + rfAnnualy)**(1/252)-1

#########################################################################################
#                             Test Runs on Both Models
#########################################################################################

if runTests:

    # Select random start index
    startIndex = 500
    endIndex = startIndex+700

    # Start SAA model
    print("\nTesting SAA:\n")
    modelSAA = TrackingModelSAA(returnsAssets=assetsReturns[startIndex:endIndex,:],
                                returnsIndex=indexReturns[startIndex:endIndex],
                                beta=beta,
                                rho=rho,
                                alpha=alphaDaily,
                                rf=rfDaily)
    resultsSAA = modelSAA.solve();
    print(resultsSAA)

    # Now we test whether the we approximate the objective correctly
    print("\nTesting objective approximation:\n")
    wSAA = np.array(resultsSAA.iloc[0,6:], dtype=np.float32)
    approx = modelSAA.approximateObjective(assetsReturns[startIndex:endIndex,:], indexReturns[startIndex:endIndex], wSAA)
    true = resultsSAA.iloc[0,0]
    print("True = {}, Approximated = {}".format(true, approx))

    # Start DRO model
    print("\nTesting DRO:\n")
    epsCollection = np.concatenate(([0], epsCollection), axis=0)
    modelDRO = TrackingModelDRO(returnsAssets=assetsReturns[startIndex:endIndex,:],
                                returnsIndex=indexReturns[startIndex:endIndex],
                                beta=beta,
                                rho=rho,
                                alpha=alphaDaily,
                                rf=rfDaily)
    resultsDRO = modelDRO.solve(epsCollection=epsCollection, rhoCollection=np.array([rho]),
                                    betaCollection=np.array([beta]), progressBar=True);
    print(resultsDRO)

#########################################################################################
#                Experiment 1 (Sensitivity to Wasserstein Radius)
#########################################################################################

if runExperiment1:

    print("\nRunning Experiment 1:\n")

    # -------- MODEL ----------

    alphaDaily = (1 + excessReturnAnually)**(1/252)-1
    rfDaily = (1 + rfAnnualy)**(1/252)-1
    rhoCollection=np.array([rho])
    betaCollection=np.array([beta])

    # -------- ADJUSTABLE ---------

    epsCollection = 10**np.linspace(-3, 1, 30)
    epsCollection = np.concatenate(([0], epsCollection), axis=0)
    totalEps = len(epsCollection)
    trainingSizes = [63, 126, 189, 252, 378, 504]   # Training sizes (in days) [1 quarter, 2 quarter, ..., 10 quarter
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

  # Initialize model (will never use more than 1000 observations -> memory is bounded)
    MODEL = TrackingModelDRO(returnsAssets=assetsReturns[:1000,:], returnsIndex=indexReturns[:1000], beta=beta, rho=rho, alpha=alphaDaily, rf=rfDaily);
    PM = PerformanceMetrics()

    # Start the loop (takes approximately 4 hours)
    with tqdm(total=nSimulations*len(trainingSizes), disable=False) as pbar:

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
                MODEL.setData(returnsAssets=assetsReturns[startIndex:endIndex,:], returnsIndex=indexReturns[startIndex:endIndex], beta=beta, rho=rho, alpha=alphaDaily, rf=rfDaily)

                # Solve it for all epsilon
                results = MODEL.solve(epsCollection=epsCollection, rhoCollection=rhoCollection,
                                        betaCollection=betaCollection, progressBar=False);

                for j in range(totalEps):

                    # Set weights (see displacement factor - in this case 7 - from the model file)
                    w = np.array(results.iloc[j,7:].values, dtype=np.float32)

                    # Save weights
                    Weights_vs_Wasserstein[h,j,:] += w

                    # Set optimal portfolio (necessary before running testPortfolio)
                    MODEL.setOptimalPortfolio(w)

                    # Test in-sample
                    assetsPathsIS, indexIS, enhancedIndexIS, portfolioIS = MODEL.testPortfolio(assetsReturns[startIndex:endIndex,:],
                                                                                            indexReturns[startIndex:endIndex], plot=False,
                                                                                            dataName="S&P500")

                    # Test out-of-sample
                    assetsPathsOoS, indexOoS, enhancedIndexOoS, portfolioOoS = MODEL.testPortfolio(assetsReturns[windowSize-testSize:windowSize,:],
                                                                                            indexReturns[windowSize-testSize:windowSize], plot=False,
                                                                                            dataName="S&P500")

                    # Compute metrics for the first run
                    PM.setData(portfolio=portfolioIS, index=indexIS, enhancedIndex=enhancedIndexIS)
                    metricsRecordings_IS = PM.getMetrics(rho=rho, beta=beta)
                    PM.setData(portfolio=portfolioOoS, index=indexOoS, enhancedIndex=enhancedIndexOoS)
                    metricsRecordings_OoS = PM.getMetrics(rho=rho, beta=beta)
                    metricsRecordings_IS['Objective'] = results.iloc[j,0]
                    metricsRecordings_OoS['Objective'] = MODEL.approximateObjective(assetsReturns[windowSize-testSize:windowSize,:], indexReturns[windowSize-testSize:windowSize], w)

                    # Prepare storage of all performance metrics
                    for k, key in enumerate(metricsRecordings_IS):
                        IS_statistics[h,i,j,k] = metricsRecordings_IS[key]
                        OoS_statistics[h,i,j,k] = metricsRecordings_OoS[key]

                # Update progress bar
                pbar.update(1)

    # Save training sizes as list for recovery
    aux = "_".join(str(e) for e in trainingSizes)

    # ------- Save for Wasserstein vs Weights -------
    np.savetxt("./Results/Chapter4_TrackingCVaR/Chapter4_Experiment1_TrackingModel_WassersteinWeights_T_{}_P_{}_{}_S_{}_recover_{}_{}_{}.csv".format(aux,
                                                                                betaCollection[0],
                                                                                rhoCollection[0],
                                                                                nSimulations,
                                                                                len(trainingSizes),
                                                                                len(epsCollection),
                                                                                assetsReturns.shape[1]+1), Weights_vs_Wasserstein.reshape(-1), fmt='%.18e', delimiter=' ')

    # ------- Save all results -------
    a,b,c,d = IS_statistics.shape
    np.savetxt("./Results/Chapter4_TrackingCVaR/Chapter4_Experiment1_TrackingModel_IS_statistics_T_{}_P_{}_{}_S_{}_recover_{}_{}_{}_{}.csv".format(aux,
                                                                                                        beta,
                                                                                                        rho,
                                                                                                        nSimulations,
                                                                                                        a, b, c, d), IS_statistics.reshape(-1), fmt='%.18e', delimiter=' ')
    np.savetxt("./Results/Chapter4_TrackingCVaR/Chapter4_Experiment1_TrackingModel_OoS_statistics_T_{}_P_{}_{}_S_{}_recover_{}_{}_{}_{}.csv".format(aux,
                                                                                                        beta,
                                                                                                        rho,
                                                                                                        nSimulations,
                                                                                                        a, b, c, d), OoS_statistics.reshape(-1), fmt='%.18e', delimiter=' ')

    # -------- Set reference counters to 0 and force garbage collection -------- #
    del IS_statistics
    del OoS_statistics
    del Weights_vs_Wasserstein
    del MODEL
    del PM
    gc.collect()

#########################################################################################
#                Experiment 2 (Sensitivity to Choice of Historical Samples)
#########################################################################################

if runExperiment2:

    print("\nRunning Experiment 2:\n")

    # -------- MODEL PARAMETERS ---------

    # Conversions (should not be modified)
    alpha = (1 + excessReturnAnually)**(1/252)-1
    rf = (1 + rfAnnualy)**(1/252)-1
    rhoCollection=np.array([rho])
    betaCollection=np.array([beta])

    # -------- ADJUSTABLE ---------

    epsCollection = 10**np.linspace(-3, 0, 20)
    epsCollection = np.concatenate(([0], epsCollection), axis=0)
    totalEps = len(epsCollection)
    trainingSizes = np.linspace(63,63*10,10, dtype=np.int16)              # Check sensitivity to choice of training data size N (training size of 1000 takes approx. 16 min. for 200 simulation)
    testSize = 126                                                        # Test on 6 months of data (2 quarter)
    validationFraction = 0.20                                             # Use 10% data to find the optimal Wasserstein radius
    nModels = 2                                                           # We compare SAA and DRO

    # -------- ALLOCATE MEMORY --------

    Certificate = np.zeros((nModels, len(trainingSizes), nSimulations))
    J = np.zeros((nModels, len(trainingSizes), nSimulations))
    epsOpt = np.zeros((len(trainingSizes), nSimulations))

    # -------- START ROLLING-WINDOW --------

    # Initialize model (will never use more than 1000 observations)
    MODEL = TrackingModelDRO(returnsAssets=assetsReturns[:1000,:], returnsIndex=indexReturns[:1000], beta=beta, rho=rho, alpha=alpha, rf=rf);

    with tqdm(total=nSimulations*len(trainingSizes), disable=False) as pbar:

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

                # Set data
                MODEL.setData(returnsAssets=assetsReturns[startIndex:endIndex,:], returnsIndex=indexReturns[startIndex:endIndex], beta=beta, rho=rho, alpha=alpha, rf=rf)

                # Solve it for all epsilon
                results = MODEL.solve(epsCollection=epsCollection, rhoCollection=rhoCollection,
                                        betaCollection=betaCollection, progressBar=False);

                # Create aray to find optimal radius
                candidates = np.zeros(totalEps-1)

                # Use validation set to obtain validation performance
                for j in range(1,totalEps):

                    # Set weights
                    wDRO = np.array(results.iloc[j,7:].values, dtype=np.float32)

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
                pbar.update(1)

    # Save results
    a,b,c = Certificate.shape
    np.savetxt("./Results/Chapter4_TrackingCVaR/Chapter4_Experiment2_TrackingModel_Certificate_recover_{}_{}_{}.csv".format(a,b,c),
            Certificate.reshape(-1), fmt='%.18e', delimiter=' ')

    a,b,c = J.shape
    np.savetxt("./Results/Chapter4_TrackingCVaR/Chapter4_Experiment2_TrackingModel_J_recover_{}_{}_{}.csv".format(a,b,c),
            J.reshape(-1), fmt='%.18e', delimiter=' ')

    a,b = epsOpt.shape
    np.savetxt("./Results/Chapter4_TrackingCVaR/Chapter4_Experiment2_TrackingModel_epsOpt_recover_{}_{}.csv".format(a,b),
            epsOpt.reshape(-1), fmt='%.18e', delimiter=' ')