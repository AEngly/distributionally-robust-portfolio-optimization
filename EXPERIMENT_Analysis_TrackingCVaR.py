"""
File: DATA_ReformatData.py
Author: Andreas Engly
Date: 30-11-2023
Description: This file generates the results for Wasserstein-based DRO of ITM model used in the thesis.

Dependencies:
- See below.

Inputs:
- In order to get the right results, the model parameters must be modified (look e.g. at ExperimentLog.txt)).

Output:
- The results are saved into .csv-files. They are reshaped into 1D-arrays and need to be recovered with dimension specified in ExperimentLog.txt.

Note:
- No additional notes.

"""

# Load dependencies
import datetime as dt
import numpy as np
from mosek.fusion import *
from tqdm import tqdm
import math
import gc
from sys import getsizeof
from tqdm import tqdm
import warnings
warnings.simplefilter("error")

# Imports from module
from EITP.Models.ITMSAA import ITMSAA as ITMSAA;
from EITP.Models.ITMDRO import ITMDRO as ITMDRO;
from EITP.PerformanceEvaluation.QuantitativeStatistics import PerformanceMetrics;
from EITP.DataHandlers.DataLoader import DataLoader;
from EITP.Auxiliaries.Logger import write_parameters_to_file;

# Print that script is starting
print("\n#########################################################################################\n")
print("                   Reproducing Experiment Results for DRC-W ITM                              ")
print("\n#########################################################################################\n")

#########################################################################################
#                             Loading Market Data
#########################################################################################

# Start by instantiating the data loader
dataLoader = DataLoader(path='./Data/');
allData = dataLoader.AggregateData(intersect=True, filtered=False, startDate="2000-01-01", endDate=dt.datetime.today().strftime("%Y-%m-%d"));
totalObservations = allData.shape[0]

# Format the output
dates = allData.iloc[:,0]
index = allData.iloc[1:,1]
indexReturns = allData.iloc[1:,1].values
assets = allData.iloc[1:,2:]
assetsReturns = allData.iloc[1:,2:].values # (risk-free rate is included here already)

# Then we can free priceData from the memory
del dataLoader
del allData
gc.collect()

#########################################################################################
#                             Control Experiments
#########################################################################################

# Specify whether to run experiments or not
runTests = False
runExperiment1 = False
runExperiment2 = False
runExperiment3 = True

# Specify number of simulations in each iteration of all experiments
nSimulations = 200

# Specify central parameters
rho = 0.2
beta = 0.80
excessReturnAnually = 0.03

#########################################################################################
#                             Test Runs on Both Models
#########################################################################################

if runTests:

    # Run a simple test
    print("\n#########################################################################################\n")
    print("                           Running Test on Models                                            ")
    print("\n#########################################################################################\n")

    # Set model parameters
    totalEps = 20
    startEps = -4
    endEps = -0.5
    epsCollection = np.concatenate(([0], 10**np.linspace(startEps, endEps, totalEps)), axis=0)
    alphaDaily = (1 + excessReturnAnually)**(1/252)-1

    # Run a simple test
    startIndex = 230
    endIndex = startIndex + 1000
    print("\nTesting SAA:\n")
    modelSAA = ITMSAA(returnsAssets=assetsReturns[startIndex:endIndex,:],
                                returnsIndex=indexReturns[startIndex:endIndex],
                                beta=beta,
                                rho=rho,
                                alpha=alphaDaily)
    resultsSAA = modelSAA.solve()
    print(resultsSAA)
    print("\nTesting DRO:\n")

    modelDRO = ITMDRO(returnsAssets=assetsReturns[startIndex:endIndex,:],
                                returnsIndex=indexReturns[startIndex:endIndex],
                                beta=beta,
                                rho=rho,
                                alpha=alphaDaily)
    resultsDRO = modelDRO.solve(epsCollection=epsCollection, rhoCollection=np.array([rho]),
                betaCollection=np.array([beta]), progressBar=True)
    print(resultsDRO)

    # Remove MODEL from memory
    del modelSAA
    del modelDRO
    del resultsSAA
    del resultsDRO
    gc.collect()

#########################################################################################
#                Experiment 1 (Sensitivity to Wasserstein Radius)
#########################################################################################

if runExperiment1:

    print("\n#########################################################################################\n")
    print("     Experiment 1: Investigate Changes in Portfolio Weights (Approximately 3h 10m)           ")
    print("\n#########################################################################################\n")

    # -------- MODEL ----------
    alphaDaily = (1 + excessReturnAnually)**(1/252)-1
    rhoCollection=np.array([rho])
    betaCollection=np.array([beta])

    # -------- ADJUSTABLE ---------
    totalNonZeroEps = 40
    startEps = -9
    endEps = 1
    epsCollection = np.concatenate(([0], 10**np.linspace(startEps, endEps, totalNonZeroEps)), axis=0)
    trainingSizes = [63, 126, 189, 252, 504, 756]
    testSize = 63                                  # Test on 6 months of data (2 quarters)
    totalEps = len(epsCollection)

    # -------- PREPARE DATA COLLECTION --------
    totalMetrics = 21

    IS_statistics = np.zeros((len(trainingSizes), nSimulations, len(epsCollection), totalMetrics))
    OoS_statistics = np.zeros((len(trainingSizes), nSimulations, len(epsCollection), totalMetrics))
    Weights_vs_Wasserstein = np.zeros((len(trainingSizes), len(epsCollection), assetsReturns.shape[1]))

    # -------- START ROLLING-WINDOW --------
    # Initialize model (will never use more than 1000 observations)
    MODEL = ITMDRO(returnsAssets=assetsReturns[:1000,:], returnsIndex=indexReturns[:1000], beta=beta, rho=rho, alpha=alphaDaily);
    PM = PerformanceMetrics()

    # Make sure

    with tqdm(total=nSimulations*len(trainingSizes), disable=False) as pbar:

        # Calculate maximum window size to make sure all evaluations are on the same out-of-sample set
        windowSizeMax = max(trainingSizes) + testSize

        # Start the actual experiment
        for h, trainingSize in enumerate(trainingSizes):

            rollingMax = totalObservations - windowSizeMax
            slideSize = int(rollingMax/nSimulations)
            increments = np.arange(0,rollingMax, slideSize)[:nSimulations]
            totalIncrements = len(increments)
            windowSize = trainingSize + testSize

            for i, shift in enumerate(increments):

                # Shift the rolling window
                startIndex = shift + (windowSizeMax - windowSize)
                endIndex = shift + windowSizeMax - testSize

                # Instantiate the model
                MODEL.setData(returnsAssets=assetsReturns[startIndex:endIndex,:], returnsIndex=indexReturns[startIndex:endIndex], beta=beta, rho=rho, alpha=alphaDaily)

                # Solve it for all epsilon
                results = MODEL.solve(epsCollection=epsCollection, rhoCollection=rhoCollection,
                                        betaCollection=betaCollection, progressBar=False);

                for j in range(totalEps):

                    # Set weights (see displacement factor - in this case 7 - from the model file)
                    w = np.array(results.iloc[j,7:].values, dtype=np.float32)

                    # Save weights
                    Weights_vs_Wasserstein[h,j,:] += w

                    # Set optimal portfolio
                    MODEL.setOptimalPortfolio(w)

                    # Test in-sample
                    assetsPathsIS, indexIS, enhancedIndexIS, portfolioIS = MODEL.testPortfolio(assetsReturns[startIndex:endIndex,:],
                                                                                            indexReturns[startIndex:endIndex], plot=False,
                                                                                            dataName="S&P500")

                    # Test out-of-sample
                    assetsPathsOoS, indexOoS, enhancedIndexOoS, portfolioOoS = MODEL.testPortfolio(assetsReturns[endIndex:endIndex+testSize,:],
                                                                                            indexReturns[endIndex:endIndex+testSize], plot=False,
                                                                                            dataName="S&P500")

                    # Compute metrics for in-sample
                    PM.setData(portfolio=portfolioIS, index=indexIS, enhancedIndex=enhancedIndexIS)
                    metricsRecordings_IS = PM.getMetrics(rho=rho, beta=beta)

                    # Compute metric for out-of-sample
                    PM.setData(portfolio=portfolioOoS, index=indexOoS, enhancedIndex=enhancedIndexOoS)
                    metricsRecordings_OoS = PM.getMetrics(rho=rho, beta=beta)

                    # Respectively log and calculate the performance in terms of the objective
                    metricsRecordings_IS['Objective'] = results.iloc[j,0]
                    metricsRecordings_OoS['Objective'] = MODEL.approximateObjective(assetsReturns[endIndex:endIndex+testSize,:], indexReturns[endIndex:endIndex+testSize], w)

                    # Prepare storage of all performance metrics
                    for k, key in enumerate(metricsRecordings_IS):
                        IS_statistics[h,i,j,k] = metricsRecordings_IS[key]
                        OoS_statistics[h,i,j,k] = metricsRecordings_OoS[key]

                # Update progress bar
                pbar.update(1)

    # Save training sizes as list for recovery
    aux = "_".join(str(e) for e in trainingSizes)

    # Get the metrics used
    columns = list(metricsRecordings_IS.keys())

    # Create logging string
    line0 = "fileName: " + "ITMDRO_WassersteinWeights" + "\n"
    line1 = "alphaAnnualy: " + str(excessReturnAnually) + "\n"
    line2 = "nSimulations: " + str(nSimulations) + "\n"
    line3 = "nAssets: " + str(assetsReturns.shape[1]+1) + "\n"
    line4 = "nEps: " + str(len(epsCollection)) + "\n"
    line5 = "nBetas: " + str(len(betaCollection)) + "\n"
    line6 = "nRhos: " + str(len(rhoCollection)) + "\n"
    line7 = "nTrainingSizes: " + str(len(trainingSizes)) + "\n"
    line8 = "epsCollection: " + "np.concatenate(([0], 10**np.linspace({}, {}, {})), axis=0)".format(startEps, endEps, totalEps) + "\n"
    line9 = "betaCollection: " + ",".join([str(round(elem,5)) for elem in betaCollection]) + "\n"
    line10 = "rhoCollection: " + ",".join([str(round(elem,5)) for elem in rhoCollection]) + "\n"
    line11 = "trainingSizes: " + ",".join([str(round(elem,5)) for elem in trainingSizes]) + "\n"
    line12 = "nStatistics: " + str(columns) + "\n"
    line13 = "testSize: " + str(testSize) + "\n"
    line14 = "recover: " + ",".join([str(elem) for elem in Weights_vs_Wasserstein.shape]) + "\n"
    parameters = line0 + line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9 + line10 + line11 + line12 + line13 + line14

    # Save results
    write_parameters_to_file(Weights_vs_Wasserstein.reshape(-1), parameters, file_name="ITMDRO_WassersteinWeights", folder_path="./Results/Chapter4_TrackingCVaR/", expId=1)

    # Create logging string
    line0 = "fileName: " + "ITMDRO_IS" + "\n"
    line1 = "alphaAnnualy: " + str(excessReturnAnually) + "\n"
    line2 = "nSimulations: " + str(nSimulations) + "\n"
    line3 = "nAssets: " + str(assetsReturns.shape[1]+1) + "\n"
    line4 = "nEps: " + str(len(epsCollection)) + "\n"
    line5 = "nBetas: " + str(len(betaCollection)) + "\n"
    line6 = "nRhos: " + str(len(rhoCollection)) + "\n"
    line7 = "nTrainingSizes: " + str(len(trainingSizes)) + "\n"
    line8 = "epsCollection: " + "np.concatenate(([0], 10**np.linspace({}, {}, {})), axis=0)".format(startEps, endEps, totalEps) + "\n"
    line9 = "betaCollection: " + ",".join([str(round(elem,5)) for elem in betaCollection]) + "\n"
    line10 = "rhoCollection: " + ",".join([str(round(elem,5)) for elem in rhoCollection]) + "\n"
    line11 = "trainingSizes: " + ",".join([str(round(elem,5)) for elem in trainingSizes]) + "\n"
    line12 = "nStatistics: " + ",".join(columns) + "\n"
    line13 = "testSize: " + str(testSize) + "\n"
    line14 = "recover: " + ",".join([str(elem) for elem in IS_statistics.shape]) + "\n"
    parameters = line0 + line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9 + line10 + line11 + line12 + line13 + line14

    # Save results
    write_parameters_to_file(IS_statistics.reshape(-1), parameters, file_name="ITMDRO_IS", folder_path="./Results/Chapter4_TrackingCVaR/", expId=1)

    # Create logging string
    line0 = "fileName: " + "ITMDRO_OoS" + "\n"
    line1 = "alphaAnnualy: " + str(excessReturnAnually) + "\n"
    line2 = "nSimulations: " + str(nSimulations) + "\n"
    line3 = "nAssets: " + str(assetsReturns.shape[1]+1) + "\n"
    line4 = "nEps: " + str(len(epsCollection)) + "\n"
    line5 = "nBetas: " + str(len(betaCollection)) + "\n"
    line6 = "nRhos: " + str(len(rhoCollection)) + "\n"
    line7 = "nTrainingSizes: " + str(len(trainingSizes)) + "\n"
    line8 = "epsCollection: " + "np.concatenate(([0], 10**np.linspace({}, {}, {})), axis=0)".format(startEps, endEps, totalEps) + "\n"
    line9 = "betaCollection: " + ",".join([str(round(elem,5)) for elem in betaCollection]) + "\n"
    line10 = "rhoCollection: " + ",".join([str(round(elem,5)) for elem in rhoCollection]) + "\n"
    line11 = "trainingSizes: " + ",".join([str(round(elem,5)) for elem in trainingSizes]) + "\n"
    line12 = "nStatistics: " + ",".join(columns) + "\n"
    line13 = "testSize: " + str(testSize) + "\n"
    line14 = "recover: " + ",".join([str(elem) for elem in OoS_statistics.shape]) + "\n"
    parameters = line0 + line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9 + line10 + line11 + line12 + line13 + line14

    # Save results
    write_parameters_to_file(OoS_statistics.reshape(-1), parameters, file_name="ITMDRO_OoS", folder_path="./Results/Chapter4_TrackingCVaR/", expId=1)

    # Force garbage collection
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

    print("\n#########################################################################################\n")
    print("                     Experiment 2: Investigate Sensitivity to Samples                        ")
    print("\n#########################################################################################\n")


    # -------- MODEL PARAMETERS ---------

    # Adjustable
    totalEps = 40
    startEps = -9
    endEps = 1
    epsCollection = 10**np.linspace(startEps, endEps, totalEps)
    epsCollection = np.concatenate(([0], epsCollection), axis=0)

    # Conversions (should not be modified)
    rhoCollection=np.array([rho])
    betaCollection=np.array([beta])
    alpha = (1 + excessReturnAnually)**(1/252)-1

    # -------- ADJUSTABLE ---------

    trainingSizes = np.linspace(63,63*8,8, dtype=np.int16)                # Check sensitivity to choice of training data size N (training size of 1000 takes approx. 16 min. for 200 simulation)
    testSize = 63                                                         # Test on 6 months of data (2 quarters)                                # Test on 6 months of data (2 quarter)
    validationFraction = 0.15                                             # Use 15% data to find the optimal Wasserstein radius
    nModels = 2                                                           # We compare SAA and DRO

    # -------- ALLOCATE MEMORY --------

    Certificate = np.zeros((nModels, len(trainingSizes), nSimulations))
    J = np.zeros((nModels, len(trainingSizes), nSimulations))
    epsOpt = np.zeros((len(trainingSizes), nSimulations))

    # -------- START ROLLING-WINDOW --------

    # MAke sure tqdm is fresh
    tqdm._instances.clear()

    # Initialize model (will never use more than 1000 observations)
    MODEL = ITMDRO(returnsAssets=assetsReturns[:1000,:], returnsIndex=indexReturns[:1000], beta=beta, rho=rho, alpha=alpha);

    with tqdm(total=nSimulations*len(trainingSizes), disable=False) as pbar:

        # Calculate maximum window size to make sure all evaluations are on the same out-of-sample set
        windowSizeMax = max(trainingSizes) + testSize

        # Start actual experiment
        for h, trainingSize in enumerate(trainingSizes):

            validationSize = math.floor(trainingSize*validationFraction)
            adjustedTrainingSize = trainingSize - validationSize
            windowSize = adjustedTrainingSize + testSize + validationSize
            rollingMax = totalObservations - windowSizeMax
            slideSize = int(rollingMax/nSimulations)
            increments = np.arange(0,rollingMax, slideSize)[:nSimulations]
            totalIncrements = len(increments)

            for i, shift in enumerate(increments):

                # Control moving window (training)
                startTrain = shift + (windowSizeMax - windowSize)
                endTrain = shift + windowSizeMax - testSize - validationSize

                # Control moving window (validation)
                startValidate = shift + (windowSizeMax - windowSize) + trainingSize
                endValidate = shift + (windowSizeMax - windowSize) + trainingSize + validationSize

                # Control moving window (testing)
                startTest = shift + windowSizeMax - testSize
                endTest = shift + windowSizeMax

                # Control moving window (retrain)
                startFullTrain = startTrain
                endFullTrain = endTrain + validationSize

                # Set data
                MODEL.setData(returnsAssets=assetsReturns[startTrain:endTrain,:], returnsIndex=indexReturns[startTrain:endTrain], beta=beta, rho=rho, alpha=alpha)

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
                    candidates[j-1] = MODEL.approximateObjective(assetsReturns[startValidate:endValidate,:],
                                                                indexReturns[startValidate:endValidate], wDRO)

                # Get optimal radius
                indexEpsOpt = np.argmin(candidates)
                epsOpt[h,i] = epsCollection[indexEpsOpt+1]

                # Retrain with optimal radius
                MODEL.setData(returnsAssets=assetsReturns[startFullTrain:endFullTrain,:], returnsIndex=indexReturns[startFullTrain:endFullTrain], beta=beta, rho=rho, alpha=alpha)
                results = MODEL.solve(epsCollection=np.array([0] + [epsOpt[h,i]]), rhoCollection=rhoCollection,
                                        betaCollection=betaCollection, progressBar=False);

                # Set portfolio
                wOptSAA = np.array(results.iloc[0,7:].values, dtype=np.float64)
                wOptDRO = np.array(results.iloc[1,7:].values, dtype=np.float64)

                # Save in-sample performance
                Certificate[0,h,i] = results.iloc[0,0]
                Certificate[1,h,i] = results.iloc[1,0]

                # Approximate out-of-sample performance
                J[0,h,i] = MODEL.approximateObjective(assetsReturns[startTest:endTest,:],
                                                                indexReturns[startTest:endTest], wOptSAA)
                J[1,h,i] = MODEL.approximateObjective(assetsReturns[startTest:endTest,:],
                                                                indexReturns[startTest:endTest], wOptDRO)

                # Update progress bar
                pbar.update(1)

    # Create logging string
    line0 = "fileName: " + "ITMDRO_Certificate" + "\n"
    line1 = "alphaAnnualy: " + str(excessReturnAnually) + "\n"
    line2 = "nSimulations: " + str(nSimulations) + "\n"
    line3 = "nAssets: " + str(assetsReturns.shape[1]+1) + "\n"
    line4 = "nEps: " + str(len(epsCollection)) + "\n"
    line5 = "nBetas: " + str(len(betaCollection)) + "\n"
    line6 = "nRhos: " + str(len(rhoCollection)) + "\n"
    line7 = "nTrainingSizes: " + str(len(trainingSizes)) + "\n"
    line8 = "epsCollection: " + "np.concatenate(([0], 10**np.linspace({}, {}, {})), axis=0)".format(startEps, endEps, totalEps) + "\n"
    line9 = "betaCollection: " + ",".join([str(round(elem,5)) for elem in betaCollection]) + "\n"
    line10 = "rhoCollection: " + ",".join([str(round(elem,5)) for elem in rhoCollection]) + "\n"
    line11 = "trainingSizes: " + ",".join([str(round(elem,5)) for elem in trainingSizes]) + "\n"
    line12 = "testSize: " + str(testSize) + "\n"
    line13 = "recover: " + ",".join([str(elem) for elem in Certificate.shape]) + "\n"
    certificateParameters = line0 + line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9 + line10 + line11 + line12 + line13

    # Save results
    write_parameters_to_file(Certificate.reshape(-1), certificateParameters, file_name="ITMDRO_Certificate", folder_path="./Results/Chapter4_TrackingCVaR/", expId=2)

    # Create logging string
    line0 = "fileName: " + "ITMDRO_J" + "\n"
    line1 = "alphaAnnualy: " + str(excessReturnAnually) + "\n"
    line2 = "nSimulations: " + str(nSimulations) + "\n"
    line3 = "nAssets: " + str(assetsReturns.shape[1]+1) + "\n"
    line4 = "nEps: " + str(len(epsCollection)) + "\n"
    line5 = "nBetas: " + str(len(betaCollection)) + "\n"
    line6 = "nRhos: " + str(len(rhoCollection)) + "\n"
    line7 = "nTrainingSizes: " + str(len(trainingSizes)) + "\n"
    line8 = "epsCollection: " + "np.concatenate(([0], 10**np.linspace({}, {}, {})), axis=0)".format(startEps, endEps, totalEps) + "\n"
    line9 = "betaCollection: " + ",".join([str(round(elem,5)) for elem in betaCollection]) + "\n"
    line10 = "rhoCollection: " + ",".join([str(round(elem,5)) for elem in rhoCollection]) + "\n"
    line11 = "trainingSizes: " + ",".join([str(round(elem,5)) for elem in trainingSizes]) + "\n"
    line12 = "testSize: " + str(testSize) + "\n"
    line13 = "recover: " + ",".join([str(elem) for elem in J.shape]) + "\n"
    JParameters = line0 + line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9 + line10 + line11 + line12 + line13

    # Save results
    write_parameters_to_file(J.reshape(-1), JParameters, file_name="ITMDRO_J", folder_path="./Results/Chapter4_TrackingCVaR/", expId=2)

    # Create logging string
    line0 = "fileName: " + "ITMDRO_epsOpt" + "\n"
    line1 = "alphaAnnualy: " + str(excessReturnAnually) + "\n"
    line2 = "nSimulations: " + str(nSimulations) + "\n"
    line3 = "nAssets: " + str(assetsReturns.shape[1]+1) + "\n"
    line4 = "nEps: " + str(len(epsCollection)) + "\n"
    line5 = "nBetas: " + str(len(betaCollection)) + "\n"
    line6 = "nRhos: " + str(len(rhoCollection)) + "\n"
    line7 = "nTrainingSizes: " + str(len(trainingSizes)) + "\n"
    line8 = "epsCollection: " + "np.concatenate(([0], 10**np.linspace({}, {}, {})), axis=0)".format(startEps, endEps, totalEps) + "\n"
    line9 = "betaCollection: " + ",".join([str(round(elem,5)) for elem in betaCollection]) + "\n"
    line10 = "rhoCollection: " + ",".join([str(round(elem,5)) for elem in rhoCollection]) + "\n"
    line11 = "trainingSizes: " + ",".join([str(round(elem,5)) for elem in trainingSizes]) + "\n"
    line12 = "testSize: " + str(testSize) + "\n"
    line13 = "recover: " + ",".join([str(elem) for elem in epsOpt.shape]) + "\n"
    epsParameters = line0 + line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9 + line10 + line11 + line12 + line13

    # Save results
    write_parameters_to_file(epsOpt.reshape(-1), epsParameters, file_name="ITMDRO_epsOpt", folder_path="./Results/Chapter4_TrackingCVaR/", expId=2)

    # Force garbage collection
    del Certificate
    del J
    del epsOpt
    del MODEL
    gc.collect()


if runExperiment3:

    print("\n#########################################################################################\n")
    print("                     Experiment 3: Investigate Sensitivity to Alpha                          ")
    print("\n#########################################################################################\n")

    print(f"\n\nRunning with rho = {rho} and beta = {beta}.\n\n")

    # -------- MODEL PARAMETERS ---------

    # Adjustable
    alphaStart = 0.95
    alphaEnd = 1.15
    totalAlpha = 15
    totalEps = 25
    startEps = -9
    endEps = 0
    epsCollection = 10**np.linspace(startEps, endEps, totalEps)
    epsCollection = np.concatenate(([0], epsCollection), axis=0)
    alphaCollection = np.linspace(alphaStart,alphaEnd,totalAlpha)**(1/252) - 1

    # Conversions (should not be modified)
    rhoCollection=np.array([rho])
    betaCollection=np.array([beta])

    # -------- ADJUSTABLE ---------

    trainingSizes = np.array([63, 252])                                   # Check sensitivity to choice of training data size N (training size of 1000 takes approx. 16 min. for 200 simulation)
    testSize = 63                                                         # Test on 6 months of data (2 quarters)                                # Test on 6 months of data (2 quarter)
    validationFraction = 0.15                                             # Use 20% data to find the optimal Wasserstein radius
    nModels = 2                                                           # We compare SAA and DRO

    # -------- ALLOCATE MEMORY --------

    AlphaTotalDeviation = np.zeros((nModels, len(alphaCollection), len(trainingSizes), nSimulations))
    AlphaRMSE = np.zeros((nModels, len(alphaCollection), len(trainingSizes), nSimulations))
    AlphaWeights = np.zeros((nModels, len(trainingSizes), len(alphaCollection), assetsReturns.shape[1], nSimulations))
    AlphaWasserstein = np.zeros((nModels, len(trainingSizes), len(alphaCollection), nSimulations))
    AlphaWassersteinCertificate = np.zeros((nModels, len(trainingSizes), len(alphaCollection), nSimulations))
    epsOpt = np.zeros((len(trainingSizes), len(alphaCollection), nSimulations))

    # -------- START ROLLING-WINDOW --------

    # MAke sure tqdm is fresh
    tqdm._instances.clear()

    # Initialize model (will never use more than 1000 observations)
    MODEL = ITMDRO(returnsAssets=assetsReturns[:1000,:], returnsIndex=indexReturns[:1000], beta=beta, rho=rho, alpha=alphaCollection[0]);
    PM = PerformanceMetrics()

    with tqdm(total=nSimulations*len(trainingSizes)*len(alphaCollection), disable=False) as pbar:

        # Calculate maximum window size to make sure all evaluations are on the same out-of-sample set
        windowSizeMax = max(trainingSizes) + testSize

        # Start actual experiment
        for h, trainingSize in enumerate(trainingSizes):

            validationSize = math.floor(trainingSize*validationFraction)
            adjustedTrainingSize = trainingSize - validationSize
            windowSize = adjustedTrainingSize + testSize + validationSize
            rollingMax = totalObservations - windowSizeMax
            slideSize = int(rollingMax/nSimulations)
            increments = np.arange(0,rollingMax, slideSize)[:nSimulations]
            totalIncrements = len(increments)

            for k, alpha in enumerate(alphaCollection):
                for i, shift in enumerate(increments):

                    # Control moving window (training)
                    startTrain = shift + (windowSizeMax - windowSize)
                    endTrain = shift + windowSizeMax - testSize - validationSize

                    # Control moving window (validation)
                    startValidate = shift + (windowSizeMax - windowSize) + trainingSize
                    endValidate = shift + (windowSizeMax - windowSize) + trainingSize + validationSize

                    # Control moving window (testing)
                    startTest = shift + windowSizeMax - testSize
                    endTest = shift + windowSizeMax

                    # Control moving window (retrain)
                    startFullTrain = startTrain
                    endFullTrain = endTrain + validationSize

                    # Set data
                    MODEL.setData(returnsAssets=assetsReturns[startTrain:endTrain,:], returnsIndex=indexReturns[startTrain:endTrain], beta=beta, rho=rho, alpha=alpha)

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
                        candidates[j-1] = MODEL.approximateObjective(assetsReturns[startValidate:endValidate,:],
                                                                    indexReturns[startValidate:endValidate], wDRO)

                    # Get optimal radius
                    indexEpsOpt = np.argmin(candidates)
                    epsOpt[h,k,i] = epsCollection[indexEpsOpt+1]

                    # Retrain with optimal radius
                    MODEL.setData(returnsAssets=assetsReturns[startFullTrain:endFullTrain,:], returnsIndex=indexReturns[startFullTrain:endFullTrain], beta=beta, rho=rho, alpha=alpha)
                    results = MODEL.solve(epsCollection=np.array([0] + [epsOpt[h,k,i]]), rhoCollection=rhoCollection,
                                            betaCollection=betaCollection, progressBar=False);

                    # Set weights (see displacement factor - in this case 7 - from the model file)
                    wDRO = np.array(results.iloc[1,7:].values, dtype=np.float32)
                    wSAA = np.array(results.iloc[0,7:].values, dtype=np.float32)
                    AlphaWeights[0,h,k,:,i] = wSAA
                    AlphaWeights[1,h,k,:,i] = wDRO

                    # Set optimal portfolio for DRO
                    MODEL.setOptimalPortfolio(wDRO)

                    # Test in-sample
                    assetsPathsIS, indexIS, enhancedIndexIS, portfolioIS = MODEL.testPortfolio(assetsReturns[startFullTrain:endFullTrain,:],
                                                                                            indexReturns[startFullTrain:endFullTrain], plot=False,
                                                                                            dataName="S&P500")

                    # Test out-of-sample
                    assetsPathsOoS, indexOoS, enhancedIndexOoS, portfolioOoS = MODEL.testPortfolio(assetsReturns[startTest:endTest,:],
                                                                                            indexReturns[startTest:endTest], plot=False,
                                                                                            dataName="S&P500")

                    # Compute metrics for in-sample
                    PM.setData(portfolio=portfolioIS, index=indexIS, enhancedIndex=enhancedIndexIS)
                    metricsRecordings_IS = PM.getMetrics(rho=rho, beta=beta)

                    # Compute metric for out-of-sample
                    PM.setData(portfolio=portfolioOoS, index=indexOoS, enhancedIndex=enhancedIndexOoS)
                    metricsRecordings_OoS = PM.getMetrics(rho=rho, beta=beta)

                    # Save metrics
                    AlphaTotalDeviation[1,k,h,i] = metricsRecordings_OoS['ExcessReturn']
                    AlphaRMSE[1,k,h,i] = metricsRecordings_OoS['RMSE']

                    # Now repeat but for SAA
                    MODEL.setOptimalPortfolio(wSAA)

                    # Test in-sample
                    assetsPathsIS, indexIS, enhancedIndexIS, portfolioIS = MODEL.testPortfolio(assetsReturns[startFullTrain:endFullTrain,:],
                                                                                            indexReturns[startFullTrain:endFullTrain], plot=False,
                                                                                            dataName="S&P500")

                    # Test out-of-sample
                    assetsPathsOoS, indexOoS, enhancedIndexOoS, portfolioOoS = MODEL.testPortfolio(assetsReturns[startTest:endTest,:],
                                                                                            indexReturns[startTest:endTest], plot=False,
                                                                                            dataName="S&P500")

                    # Compute metrics for in-sample
                    PM.setData(portfolio=portfolioIS, index=indexIS, enhancedIndex=enhancedIndexIS)
                    metricsRecordings_IS = PM.getMetrics(rho=rho, beta=beta)

                    # Compute metric for out-of-sample
                    PM.setData(portfolio=portfolioOoS, index=indexOoS, enhancedIndex=enhancedIndexOoS)
                    metricsRecordings_OoS = PM.getMetrics(rho=rho, beta=beta)

                    # Save metrics
                    AlphaTotalDeviation[0,k,h,i] = metricsRecordings_OoS['ExcessReturn']
                    AlphaRMSE[0,k,h,i] = metricsRecordings_OoS['RMSE']

                    # Set portfolio
                    wOptSAA = np.array(results.iloc[0,7:].values, dtype=np.float64)
                    wOptDRO = np.array(results.iloc[1,7:].values, dtype=np.float64)

                    # Approximate in-sample performance
                    AlphaWassersteinCertificate[0,h,k,i] = results.iloc[0,0]
                    AlphaWassersteinCertificate[1,h,k,i] = results.iloc[1,0]

                    # Approximate out-of-sample performance
                    AlphaWasserstein[0,h,k,i] = MODEL.approximateObjective(assetsReturns[startTest:endTest,:],
                                                                    indexReturns[startTest:endTest], wSAA)
                    AlphaWasserstein[1,h,k,i] = MODEL.approximateObjective(assetsReturns[startTest:endTest,:],
                                                                    indexReturns[startTest:endTest], wDRO)

                    # Update progress bar
                    pbar.update(1)

# We need to save these

    # Create logging string
    line0 = "fileName: " + "ITMDRO_AlphaTotalDeviation" + "\n"
    line1 = "nSimulations: " + str(nSimulations) + "\n"
    line2 = "nAssets: " + str(assetsReturns.shape[1]) + "\n"
    line3 = "nEps: " + str(len(epsCollection)) + "\n"
    line4 = "nBetas: " + str(len(betaCollection)) + "\n"
    line5 = "nRhos: " + str(len(rhoCollection)) + "\n"
    line6 = "nTrainingSizes: " + str(len(trainingSizes)) + "\n"
    line7 = "epsCollection: " + "np.concatenate(([0], 10**np.linspace({}, {}, {})), axis=0)".format(startEps, endEps, totalEps) + "\n"
    line8 = "betaCollection: " + ",".join([str(round(elem,5)) for elem in betaCollection]) + "\n"
    line9 = "alphaCollection: " + "np.linspace({},{},{})**(1/252) - 1".format(alphaStart, alphaEnd, totalAlpha) + "\n"
    line10 = "rhoCollection: " + ",".join([str(round(elem,5)) for elem in rhoCollection]) + "\n"
    line11 = "trainingSizes: " + ",".join([str(round(elem,5)) for elem in trainingSizes]) + "\n"
    line12 = "testSize: " + str(testSize) + "\n"
    line13 = "recover: " + ",".join([str(elem) for elem in AlphaTotalDeviation.shape]) + "\n"
    certificateParameters = line0 + line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9 + line10 + line11 + line12 + line13

    # Save results
    write_parameters_to_file(AlphaTotalDeviation.reshape(-1), certificateParameters, file_name="ITMDRO_AlphaTotalDeviation", folder_path="./Results/Chapter4_TrackingCVaR/", expId=3)

    # Create logging string
    line0 = "fileName: " + "ITMDRO_AlphaRMSE" + "\n"
    line1 = "nSimulations: " + str(nSimulations) + "\n"
    line2 = "nAssets: " + str(assetsReturns.shape[1]) + "\n"
    line3 = "nEps: " + str(len(epsCollection)) + "\n"
    line4 = "nBetas: " + str(len(betaCollection)) + "\n"
    line5 = "nRhos: " + str(len(rhoCollection)) + "\n"
    line6 = "nTrainingSizes: " + str(len(trainingSizes)) + "\n"
    line7 = "epsCollection: " + "np.concatenate(([0], 10**np.linspace({}, {}, {})), axis=0)".format(startEps, endEps, totalEps) + "\n"
    line8 = "betaCollection: " + ",".join([str(round(elem,5)) for elem in betaCollection]) + "\n"
    line9 = "alphaCollection: " + "np.linspace({},{},{})**(1/252) - 1".format(alphaStart, alphaEnd, totalAlpha) + "\n"
    line10 = "rhoCollection: " + ",".join([str(round(elem,5)) for elem in rhoCollection]) + "\n"
    line11 = "trainingSizes: " + ",".join([str(round(elem,5)) for elem in trainingSizes]) + "\n"
    line12 = "testSize: " + str(testSize) + "\n"
    line13 = "recover: " + ",".join([str(elem) for elem in AlphaRMSE.shape]) + "\n"
    certificateParameters = line0 + line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9 + line10 + line11 + line12 + line13

    # Save results
    write_parameters_to_file(AlphaRMSE.reshape(-1), certificateParameters, file_name="ITMDRO_AlphaRMSE", folder_path="./Results/Chapter4_TrackingCVaR/", expId=3)

    # Create logging string
    line0 = "fileName: " + "ITMDRO_AlphaWeights" + "\n"
    line1 = "nSimulations: " + str(nSimulations) + "\n"
    line2 = "nAssets: " + str(assetsReturns.shape[1]) + "\n"
    line3 = "nEps: " + str(len(epsCollection)) + "\n"
    line4 = "nBetas: " + str(len(betaCollection)) + "\n"
    line5 = "nRhos: " + str(len(rhoCollection)) + "\n"
    line6 = "nTrainingSizes: " + str(len(trainingSizes)) + "\n"
    line7 = "epsCollection: " + "np.concatenate(([0], 10**np.linspace({}, {}, {})), axis=0)".format(startEps, endEps, totalEps) + "\n"
    line8 = "betaCollection: " + ",".join([str(round(elem,5)) for elem in betaCollection]) + "\n"
    line9 = "alphaCollection: " + "np.linspace({},{},{})**(1/252) - 1".format(alphaStart, alphaEnd, totalAlpha) + "\n"
    line10 = "rhoCollection: " + ",".join([str(round(elem,5)) for elem in rhoCollection]) + "\n"
    line11 = "trainingSizes: " + ",".join([str(round(elem,5)) for elem in trainingSizes]) + "\n"
    line12 = "testSize: " + str(testSize) + "\n"
    line13 = "recover: " + ",".join([str(elem) for elem in AlphaWeights.shape]) + "\n"
    certificateParameters = line0 + line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9 + line10 + line11 + line12 + line13

    # Save results
    write_parameters_to_file(AlphaWeights.reshape(-1), certificateParameters, file_name="ITMDRO_AlphaWeights", folder_path="./Results/Chapter4_TrackingCVaR/", expId=3)

    # Create logging string
    line0 = "fileName: " + "ITMDRO_AlphaWasserstein" + "\n"
    line1 = "nSimulations: " + str(nSimulations) + "\n"
    line2 = "nAssets: " + str(assetsReturns.shape[1]) + "\n"
    line3 = "nEps: " + str(len(epsCollection)) + "\n"
    line4 = "nBetas: " + str(len(betaCollection)) + "\n"
    line5 = "nRhos: " + str(len(rhoCollection)) + "\n"
    line6 = "nTrainingSizes: " + str(len(trainingSizes)) + "\n"
    line7 = "epsCollection: " + "np.concatenate(([0], 10**np.linspace({}, {}, {})), axis=0)".format(startEps, endEps, totalEps) + "\n"
    line8 = "betaCollection: " + ",".join([str(round(elem,5)) for elem in betaCollection]) + "\n"
    line9 = "alphaCollection: " + "np.linspace({},{},{})**(1/252) - 1".format(alphaStart, alphaEnd, totalAlpha) + "\n"
    line10 = "rhoCollection: " + ",".join([str(round(elem,5)) for elem in rhoCollection]) + "\n"
    line11 = "trainingSizes: " + ",".join([str(round(elem,5)) for elem in trainingSizes]) + "\n"
    line12 = "testSize: " + str(testSize) + "\n"
    line13 = "recover: " + ",".join([str(elem) for elem in AlphaWasserstein.shape]) + "\n"
    certificateParameters = line0 + line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9 + line10 + line11 + line12 + line13

    # Save results
    write_parameters_to_file(AlphaWasserstein.reshape(-1), certificateParameters, file_name="ITMDRO_AlphaWasserstein", folder_path="./Results/Chapter4_TrackingCVaR/", expId=3)

    # Create logging string
    line0 = "fileName: " + "ITMDRO_AlphaWassersteinCertificate" + "\n"
    line1 = "nSimulations: " + str(nSimulations) + "\n"
    line2 = "nAssets: " + str(assetsReturns.shape[1]) + "\n"
    line3 = "nEps: " + str(len(epsCollection)) + "\n"
    line4 = "nBetas: " + str(len(betaCollection)) + "\n"
    line5 = "nRhos: " + str(len(rhoCollection)) + "\n"
    line6 = "nTrainingSizes: " + str(len(trainingSizes)) + "\n"
    line7 = "epsCollection: " + "np.concatenate(([0], 10**np.linspace({}, {}, {})), axis=0)".format(startEps, endEps, totalEps) + "\n"
    line8 = "betaCollection: " + ",".join([str(round(elem,5)) for elem in betaCollection]) + "\n"
    line9 = "alphaCollection: " + "np.linspace({},{},{})**(1/252) - 1".format(alphaStart, alphaEnd, totalAlpha) + "\n"
    line10 = "rhoCollection: " + ",".join([str(round(elem,5)) for elem in rhoCollection]) + "\n"
    line11 = "trainingSizes: " + ",".join([str(round(elem,5)) for elem in trainingSizes]) + "\n"
    line12 = "testSize: " + str(testSize) + "\n"
    line13 = "recover: " + ",".join([str(elem) for elem in AlphaWassersteinCertificate.shape]) + "\n"
    certificateParameters = line0 + line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9 + line10 + line11 + line12 + line13

    # Save results
    write_parameters_to_file(AlphaWassersteinCertificate.reshape(-1), certificateParameters, file_name="ITMDRO_AlphaWassersteinCertificate", folder_path="./Results/Chapter4_TrackingCVaR/", expId=3)

    # Create logging string
    line0 = "fileName: " + "ITMDRO_alphaEpsOpt" + "\n"
    line1 = "nSimulations: " + str(nSimulations) + "\n"
    line2 = "nAssets: " + str(assetsReturns.shape[1]) + "\n"
    line3 = "nEps: " + str(len(epsCollection)) + "\n"
    line4 = "nBetas: " + str(len(betaCollection)) + "\n"
    line5 = "nRhos: " + str(len(rhoCollection)) + "\n"
    line6 = "nTrainingSizes: " + str(len(trainingSizes)) + "\n"
    line7 = "epsCollection: " + "np.concatenate(([0], 10**np.linspace({}, {}, {})), axis=0)".format(startEps, endEps, totalEps) + "\n"
    line8 = "betaCollection: " + ",".join([str(round(elem,5)) for elem in betaCollection]) + "\n"
    line9 = "alphaCollection: " + "np.linspace({},{},{})**(1/252) - 1".format(alphaStart, alphaEnd, totalAlpha) + "\n"
    line10 = "rhoCollection: " + ",".join([str(round(elem,5)) for elem in rhoCollection]) + "\n"
    line11 = "trainingSizes: " + ",".join([str(round(elem,5)) for elem in trainingSizes]) + "\n"
    line12 = "testSize: " + str(testSize) + "\n"
    line13 = "recover: " + ",".join([str(elem) for elem in epsOpt.shape]) + "\n"
    certificateParameters = line0 + line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9 + line10 + line11 + line12 + line13

    # Save results
    write_parameters_to_file(epsOpt.reshape(-1), certificateParameters, file_name="ITMDRO_alphaEpsOpt", folder_path="./Results/Chapter4_TrackingCVaR/", expId=3)
