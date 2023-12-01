"""
Author: Andreas Heidelbach Engly (s170303)
Purpose: This file generates the results for Wasserstein-based DRO of ExcessCVaR model used in the thesis.

Inputs:
- In order to get the right results, the model parameters must be modified (look e.g. at ExperimentLog.txt)).

Outputs:
- The results are saved into .csv-files. They are reshaped into 1D-arrays and need to be recovered with dimension specified in ExperimentLog.txt.
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

# Imports from module
from EITP.Models.TrackingModelSAA import TrackingModelSAA as TrackingModelSAA;
from EITP.Models.ExcessCVaRModelSAA import ExcessCVaRModelSAA as ExcessCVaRModelSAA;
from EITP.Models.TrackingModelDRO import TrackingModelDRO as TrackingModelDRO;
from EITP.Models.ExcessCVaRModelDRO import ExcessCVaRModelDRO as ExcessCVaRModelDRO;
from EITP.PerformanceEvaluation.QuantitativeStatistics import PerformanceMetrics;
from EITP.Data.DataLoader import DataLoader;
from EITP.Auxiliaries.Logger import write_parameters_to_file;

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
del dataLoader
del priceData
gc.collect()

#########################################################################################
#                             Control Experiments
#########################################################################################

# Specify whether to run experiments or not
runTests = True
runExperiment1 = False
runExperiment2 = False

# Specify number of simulations in each iteration of all experiments
nSimulations = 200

# Specify central parameters
rho = 2
beta = 0.90
excessReturnAnually = 0
rfAnnualy = 0.02

#########################################################################################
#                             Test Runs on Both Models
#########################################################################################

if runTests:

    # Set model parameters
    totalEps = 30
    startEps = -6
    endEps = 0.5
    epsCollection = np.concatenate(([0], 10**np.linspace(startEps, endEps, totalEps)), axis=0)
    alphaDaily = (1 + excessReturnAnually)**(1/252)-1
    rfDaily = (1 + rfAnnualy)**(1/252)-1

    # Run a simple test
    startIndex = 230
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

    print("\nRunning Experiment 1:\n")

    # -------- MODEL ----------
    alphaDaily = (1 + excessReturnAnually)**(1/252)-1
    rfDaily = (1 + rfAnnualy)**(1/252)-1
    rhoCollection=np.array([rho])
    betaCollection=np.array([beta])

    # -------- ADJUSTABLE ---------
    totalEps = 50
    startEps = -6
    endEps = 0.5
    epsCollection = np.concatenate(([0], 10**np.linspace(startEps, endEps, totalEps)), axis=0)
    trainingSizes = [63, 126, 189, 252, 504]
    testSize = 126                                  # Test on 6 months of data (2 quarters)

    # -------- PREPARE DATA COLLECTION --------
    columns =    ['WassersteinRadius',
                'Objective',
                'DownsideSemiStandardDeviation',
                'RMSE',
                'MAD',
                'VaR',
                'CVaR',
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

    # Initialize model (will never use more than 1000 observations)
    MODEL = ExcessCVaRModelDRO(returnsAssets=assetsReturns[:1000,:], returnsIndex=indexReturns[:1000], beta=beta, rho=rho, alpha=alphaDaily, rf=rfDaily);
    PM = PerformanceMetrics()

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

                    # Compute metrics for the first run
                    PM.setData(portfolio=portfolioIS, index=indexIS, enhancedIndex=enhancedIndexIS)
                    metricsRecordings_IS = PM.getMetrics(rho=rho, beta=beta)
                    PM.setData(portfolio=portfolioOoS, index=indexOoS, enhancedIndex=enhancedIndexOoS)
                    metricsRecordings_OoS = PM.getMetrics(rho=rho, beta=beta)
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

    # Create logging string
    line0 = "fileName: " + "ExcessModelDRO_WassersteinWeights" + "\n"
    line1 = "nSimulations: " + str(nSimulations) + "\n"
    line2 = "nAssets: " + str(assetsReturns.shape[1]+1) + "\n"
    line3 = "nEps: " + str(len(epsCollection)) + "\n"
    line4 = "nBetas: " + str(len(betaCollection)) + "\n"
    line5 = "nRhos: " + str(len(rhoCollection)) + "\n"
    line6 = "nTrainingSizes: " + str(len(trainingSizes)) + "\n"
    line7 = "epsCollection: " + "np.concatenate(([0], 10**np.linspace({}, {}, {})), axis=0)".format(startEps, endEps, totalEps) + "\n"
    line8 = "betaCollection: " + ",".join([str(round(elem,5)) for elem in betaCollection]) + "\n"
    line9 = "rhoCollection: " + ",".join([str(round(elem,5)) for elem in rhoCollection]) + "\n"
    line10 = "trainingSizes: " + ",".join([str(round(elem,5)) for elem in trainingSizes]) + "\n"
    line11 = "nStatistics: " + str(columns) + "\n"
    line12 = "testSize: " + str(testSize) + "\n"
    line13 = "recover: " + ",".join([str(elem) for elem in Weights_vs_Wasserstein.shape]) + "\n"
    parameters = line0 + line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9 + line10 + line11 + line12 + line13

    # Save results
    write_parameters_to_file(Weights_vs_Wasserstein.reshape(-1), parameters, file_name="ExcessModelDRO_WassersteinWeights", folder_path="./Results/Chapter5_ExcessCVaR/", expId=1)

    # Create logging string
    line0 = "fileName: " + "ExcessModelDRO_IS" + "\n"
    line1 = "nSimulations: " + str(nSimulations) + "\n"
    line2 = "nAssets: " + str(assetsReturns.shape[1]+1) + "\n"
    line3 = "nEps: " + str(len(epsCollection)) + "\n"
    line4 = "nBetas: " + str(len(betaCollection)) + "\n"
    line5 = "nRhos: " + str(len(rhoCollection)) + "\n"
    line6 = "nTrainingSizes: " + str(len(trainingSizes)) + "\n"
    line7 = "epsCollection: " + "np.concatenate(([0], 10**np.linspace({}, {}, {})), axis=0)".format(startEps, endEps, totalEps) + "\n"
    line8 = "betaCollection: " + ",".join([str(round(elem,5)) for elem in betaCollection]) + "\n"
    line9 = "rhoCollection: " + ",".join([str(round(elem,5)) for elem in rhoCollection]) + "\n"
    line10 = "trainingSizes: " + ",".join([str(round(elem,5)) for elem in trainingSizes]) + "\n"
    line11 = "nStatistics: " + ",".join(columns) + "\n"
    line12 = "testSize: " + str(testSize) + "\n"
    line13 = "recover: " + ",".join([str(elem) for elem in IS_statistics.shape]) + "\n"
    parameters = line0 + line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9 + line10 + line11 + line12 + line13

    # Save results
    write_parameters_to_file(IS_statistics.reshape(-1), parameters, file_name="ExcessModelDRO_IS", folder_path="./Results/Chapter5_ExcessCVaR/", expId=1)

    # Create logging string
    line0 = "fileName: " + "ExcessModelDRO_OoS" + "\n"
    line1 = "nSimulations: " + str(nSimulations) + "\n"
    line2 = "nAssets: " + str(assetsReturns.shape[1]+1) + "\n"
    line3 = "nEps: " + str(len(epsCollection)) + "\n"
    line4 = "nBetas: " + str(len(betaCollection)) + "\n"
    line5 = "nRhos: " + str(len(rhoCollection)) + "\n"
    line6 = "nTrainingSizes: " + str(len(trainingSizes)) + "\n"
    line7 = "epsCollection: " + "np.concatenate(([0], 10**np.linspace({}, {}, {})), axis=0)".format(startEps, endEps, totalEps) + "\n"
    line8 = "betaCollection: " + ",".join([str(round(elem,5)) for elem in betaCollection]) + "\n"
    line9 = "rhoCollection: " + ",".join([str(round(elem,5)) for elem in rhoCollection]) + "\n"
    line10 = "trainingSizes: " + ",".join([str(round(elem,5)) for elem in trainingSizes]) + "\n"
    line11 = "nStatistics: " + ",".join(columns) + "\n"
    line12 = "testSize: " + str(testSize) + "\n"
    line13 = "recover: " + ",".join([str(elem) for elem in OoS_statistics.shape]) + "\n"
    parameters = line0 + line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9 + line10 + line11 + line12 + line13

    # Save results
    write_parameters_to_file(OoS_statistics.reshape(-1), parameters, file_name="ExcessModelDRO_OoS", folder_path="./Results/Chapter5_ExcessCVaR/", expId=1)

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

    print("\nRunning Experiment 2:\n")

    # -------- MODEL PARAMETERS ---------

    # Adjustable
    totalEps = 40
    startEps = -7
    endEps = 0
    epsCollection = 10**np.linspace(startEps, endEps, totalEps)
    epsCollection = np.concatenate(([0], epsCollection), axis=0)

    # Conversions (should not be modified)
    rhoCollection=np.array([rho])
    betaCollection=np.array([beta])
    alpha = (1 + excessReturnAnually)**(1/252)-1
    rf = (1 + rfAnnualy)**(1/252)-1

    # -------- ADJUSTABLE ---------

    trainingSizes = np.linspace(63,63*10,10, dtype=np.int16)              # Check sensitivity to choice of training data size N (training size of 1000 takes approx. 16 min. for 200 simulation)
    testSize = 126                                                        # Test on 6 months of data (2 quarters)                                # Test on 6 months of data (2 quarter)
    validationFraction = 0.20                                             # Use 20% data to find the optimal Wasserstein radius
    nModels = 2                                                           # We compare SAA and DRO

    # -------- ALLOCATE MEMORY --------

    Certificate = np.zeros((nModels, len(trainingSizes), nSimulations))
    J = np.zeros((nModels, len(trainingSizes), nSimulations))
    epsOpt = np.zeros((len(trainingSizes), nSimulations))

    # -------- START ROLLING-WINDOW --------

    # Initialize model (will never use more than 1000 observations)
    MODEL = ExcessCVaRModelDRO(returnsAssets=assetsReturns[:1000,:], returnsIndex=indexReturns[:1000], beta=beta, rho=rho, alpha=alpha, rf=rf);

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

    # Create logging string
    line1 = "alphaAnnualy: " + str(excessReturnAnually) + "\n"
    line2 = "riskFreeAnnualy: " + str(rfAnnualy) + "\n"
    line3 = "nSimulations: " + str(nSimulations) + "\n"
    line4 = "nAssets: " + str(assetsReturns.shape[1]+1) + "\n"
    line5 = "nEps: " + str(len(epsCollection)) + "\n"
    line6 = "nBetas: " + str(len(betaCollection)) + "\n"
    line7 = "nRhos: " + str(len(rhoCollection)) + "\n"
    line8 = "nTrainingSizes: " + str(len(trainingSizes)) + "\n"
    line9 = "epsCollection: " + "np.concatenate(([0], 10**np.linspace({}, {}, {})), axis=0)".format(startEps, endEps, totalEps) + "\n"
    line10 = "betaCollection: " + ",".join([str(round(elem,5)) for elem in betaCollection]) + "\n"
    line11 = "rhoCollection: " + ",".join([str(round(elem,5)) for elem in rhoCollection]) + "\n"
    line12 = "trainingSizes: " + ",".join([str(round(elem,5)) for elem in trainingSizes]) + "\n"
    line13 = "testSize: " + str(testSize) + "\n"
    line14 = "recover: " + ",".join([str(elem) for elem in Certificate.shape]) + "\n"
    certificateParameters = line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9 + line10 + line11 + line12 + line13 + line14

    # Save results
    write_parameters_to_file(Certificate.reshape(-1), certificateParameters, file_name="ExcessModelDRO_Certificate", folder_path="./Results/Chapter5_ExcessCVaR/", expId=2)

    # Create logging string
    line1 = "alphaAnnualy: " + str(excessReturnAnually) + "\n"
    line2 = "riskFreeAnnualy: " + str(rfAnnualy) + "\n"
    line3 = "nSimulations: " + str(nSimulations) + "\n"
    line4 = "nAssets: " + str(assetsReturns.shape[1]+1) + "\n"
    line5 = "nEps: " + str(len(epsCollection)) + "\n"
    line6 = "nBetas: " + str(len(betaCollection)) + "\n"
    line7 = "nRhos: " + str(len(rhoCollection)) + "\n"
    line8 = "nTrainingSizes: " + str(len(trainingSizes)) + "\n"
    line9 = "epsCollection: " + "np.concatenate(([0], 10**np.linspace({}, {}, {})), axis=0)".format(startEps, endEps, totalEps) + "\n"
    line10 = "betaCollection: " + ",".join([str(round(elem,5)) for elem in betaCollection]) + "\n"
    line11 = "rhoCollection: " + ",".join([str(round(elem,5)) for elem in rhoCollection]) + "\n"
    line12 = "trainingSizes: " + ",".join([str(round(elem,5)) for elem in trainingSizes]) + "\n"
    line13 = "testSize: " + str(testSize) + "\n"
    line14 = "recover: " + ",".join([str(elem) for elem in J.shape]) + "\n"
    JParameters = line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9 + line10 + line11 + line12 + line13 + line14

    # Save results
    write_parameters_to_file(J.reshape(-1), JParameters, file_name="ExcessModelDRO_J", folder_path="./Results/Chapter5_ExcessCVaR/", expId=2)

    # Create logging string
    line1 = "alphaAnnualy: " + str(excessReturnAnually) + "\n"
    line2 = "riskFreeAnnualy: " + str(rfAnnualy) + "\n"
    line3 = "nSimulations: " + str(nSimulations) + "\n"
    line4 = "nAssets: " + str(assetsReturns.shape[1]+1) + "\n"
    line5 = "nEps: " + str(len(epsCollection)) + "\n"
    line6 = "nBetas: " + str(len(betaCollection)) + "\n"
    line7 = "nRhos: " + str(len(rhoCollection)) + "\n"
    line8 = "nTrainingSizes: " + str(len(trainingSizes)) + "\n"
    line9 = "epsCollection: " + "np.concatenate(([0], 10**np.linspace({}, {}, {})), axis=0)".format(startEps, endEps, totalEps) + "\n"
    line10 = "betaCollection: " + ",".join([str(round(elem,5)) for elem in betaCollection]) + "\n"
    line11 = "rhoCollection: " + ",".join([str(round(elem,5)) for elem in rhoCollection]) + "\n"
    line12 = "trainingSizes: " + ",".join([str(round(elem,5)) for elem in trainingSizes]) + "\n"
    line13 = "testSize: " + str(testSize) + "\n"
    line14 = "recover: " + ",".join([str(elem) for elem in epsOpt.shape]) + "\n"
    epsParameters = line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9 + line10 + line11 + line12 + line13 + line14

    # Save results
    write_parameters_to_file(epsOpt.reshape(-1), epsParameters, file_name="ExcessModelDRO_epsOpt", folder_path="./Results/Chapter5_ExcessCVaR/", expId=2)

    # Force garbage collection
    del Certificate
    del J
    del epsOpt
    del MODEL
    gc.collect()