"""
Author: Andreas Heidelbach Engly (s170303)
Purpose: This file test the risk-aversion sensitivity for RAERM.
Date: 15-01-2024

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
from sys import getsizeof
from tqdm import tqdm
import pandas as pd

# Imports from module
from EITP.Models.TrackingModelSAA import TrackingModelSAA as TrackingModelSAA;
from EITP.Models.ExcessCVaRModelSAA import ExcessCVaRModelSAA as ExcessCVaRModelSAA;
from EITP.Models.TrackingModelDRO import TrackingModelDRO as TrackingModelDRO;
from EITP.Models.ITMDRO import ITMDRO as ITMDRO;
from EITP.Models.RAERMDRO import RAERMDRO as RAERMDRO;
from EITP.Models.ExcessCVaRModelDRO import ExcessCVaRModelDRO as ExcessCVaRModelDRO;
from EITP.PerformanceEvaluation.QuantitativeStatistics import PerformanceMetrics;
from EITP.DataHandlers.DataLoader import DataLoader;
from EITP.Auxiliaries.Logger import write_parameters_to_file;

# Print that script is starting
print("\n#########################################################################################\n")
print("                           Running Backtest of RAERM                                         ")
print("\n#########################################################################################\n")

#########################################################################################
#                             Loading Market Data
#########################################################################################

# Specify start of experiment
startDate = "1999-01-01"
startDateBacktest = "2002-01-01"
endDate = dt.datetime.today().strftime("%Y-%m-%d")

# Start by instantiating the data loader
dataLoader = DataLoader(path='./Data/')
priceData = dataLoader.AggregateData(intersect=False, filtered=False, startDate=startDate, endDate=endDate);
priceData['Dates'] = pd.to_datetime(priceData['Dates'])
totalObservations = priceData.shape[0]

#########################################################################################
#                             Control Experiment
#########################################################################################

# Specify central parameters
rho = 2
beta = 0.80
excessReturnAnually = 0
alphaDaily = (1 + excessReturnAnually)**(1/252)-1
betaCollection=np.array([beta])

# Select range for risk-aversion
startRho = -2
endRho = 0.7
totalRho = 30
rhoCollection = 10**np.linspace(startRho, endRho, totalRho)
nRhos = len(rhoCollection)

# Select range to search for optimal uncertainty
startEps = -6
endEps = 1
epsCollection = np.concatenate(([0], 10**np.linspace(startEps, endEps, 30)), axis=0)
totalEps = len(epsCollection)

# Specify training size
validationPercentage = 0.15
oneQuarter = 63
trainingSizes = [oneQuarter, 4*oneQuarter]
nTrainingSizes = len(trainingSizes)

#########################################################################################
#                             Prepare Rebalance Dates
#########################################################################################

# Get all tickers
beginDate = pd.to_datetime(startDateBacktest)
endDate = pd.to_datetime("2023-10-01")

# Create a a list of first day of month
firstDoM = []

# Create a list of dates
currentDate = beginDate
while currentDate < endDate:
    firstDoM.append(currentDate)
    currentDate = currentDate + pd.DateOffset(months=3)

# Get the first date larger than or equal to the firstDoM
rebalanceDates = []
rebalanceIndices = []

# Loop through all the dates
for date in firstDoM:
    # Get the index of the first date larger than or equal to date
    idx = priceData['Dates'].searchsorted(date, side='left')
    rebalanceDates.append(priceData['Dates'].iloc[idx])
    rebalanceIndices.append(idx)

# Get the relevant dates used for training and testing the portfolio
firstDate = priceData[priceData['Dates'] == rebalanceDates[0]].copy()
lastDate = priceData[priceData['Dates'] == rebalanceDates[-1]].copy()
indexFirstDate = firstDate['Dates'].index.values[0]
indexLastDate = lastDate['Dates'].index.values[0]
allDates = priceData.iloc[indexFirstDate:indexLastDate+1,:].copy()['Dates']

# Get returns
dates = priceData.iloc[:,0]
index = priceData.iloc[:,1]
indexReturns = priceData.iloc[:,1].pct_change().dropna(axis=0).values
assets = priceData.iloc[:,2:]
assetsReturns = np.ones((priceData.iloc[:,2:].shape[0], priceData.iloc[:,2:].shape[1]))

# Allocate memory to save statistics
epsOpt = np.zeros((nRhos, nTrainingSizes, len(rebalanceIndices)))

# Allocate space for portfolio values
totalDays = allDates.shape[0]
trajectories = np.zeros((nRhos, nTrainingSizes, totalDays, 4))

# Allocate memory for statistics
nModels = 2
totalMetrics = 21
OoS_statistics = np.zeros((nModels, nRhos, nTrainingSizes, len(rebalanceIndices), totalMetrics))
IS_statistics = np.zeros((nModels, nRhos, nTrainingSizes, len(rebalanceIndices), totalMetrics))

# Initialize model and metrics engine
MODEL = RAERMDRO(returnsAssets=assetsReturns[:1000,:], returnsIndex=indexReturns[:1000], beta=beta, rho=rho, alpha=alphaDaily);
PM = PerformanceMetrics()

# Start the experiment. We do not include last rebalancing date as it defines the end of the experiment.
with tqdm(total=len(rebalanceIndices[:-1])*nTrainingSizes*nRhos, disable=False) as pbar:
    for indexRho, rho in enumerate(rhoCollection):
        for TS, trainingSize in enumerate(trainingSizes):

            # First period must be treated separately
            Tdx = 0

            # Begin backtest for new training size
            for k,idx in enumerate(rebalanceIndices[:-1]):

                # Specify size of validation set in percentage of trainingSize
                validationSize = int(validationPercentage * trainingSize)

                # Get the relevant range
                periodStartIndex = idx - trainingSize
                periodStart = priceData['Dates'].iloc[periodStartIndex]
                periodEndIndex = idx
                periodEnd = priceData['Dates'].iloc[periodEndIndex]
                nextPeriodStartIndex = rebalanceIndices[k+1]
                nextPeriodStart = priceData['Dates'].iloc[nextPeriodStartIndex]

                # Get the shares for which we have data over the entire period
                periodTickers = dataLoader.getTickerRange(startDate=periodStart.strftime("%Y-%m-%d"), endDate=nextPeriodStart.strftime("%Y-%m-%d"))
                periodTickers = list(priceData.columns[:2]) + [ticker for ticker in periodTickers if ticker in priceData.columns]

                # Some of tickers are not available from the data sources. Remove them.
                selectedPrices = priceData[priceData['Dates'] >= periodStart].copy()
                selectedPrices = selectedPrices[selectedPrices['Dates'] <= nextPeriodStart]
                selectedPrices = selectedPrices.loc[:, periodTickers]
                selectedPrices = selectedPrices.dropna(axis=1)

                # Calculate returns from selectedPrices
                indexReturns = selectedPrices.iloc[:,1].pct_change().dropna(axis=0).values
                assetsReturns = selectedPrices.iloc[:,2:].pct_change().dropna(axis=0).values

                # Set the training data
                endTrainingIndex = (trainingSize - validationSize)
                endValidationIndex = trainingSize
                MODEL.setData(returnsAssets=assetsReturns[:endTrainingIndex,:], returnsIndex=indexReturns[:endTrainingIndex], beta=beta, rho=rho, alpha=alphaDaily)

                # Solve it for all epsilon
                results = MODEL.solve(epsCollection=epsCollection, rhoCollection=np.array([rho]),
                                        betaCollection=betaCollection, progressBar=False);

                # Get the optimal epsilon
                candidates = np.zeros(totalEps)
                for jdx in range(totalEps):

                    # Get the weights
                    wDRO = np.array(results.iloc[jdx,7:].values, dtype=np.float32)

                    # Set the weights
                    MODEL.setOptimalPortfolio(wDRO)

                    # Compute certificate and J
                    candidates[jdx] = MODEL.approximateObjective(assetsReturns[endTrainingIndex:endValidationIndex,:],
                                                                indexReturns[endTrainingIndex:endValidationIndex], wDRO)


                # Get optimal radius
                indexEpsOpt = np.argmin(candidates)
                epsOpt[indexRho,TS,k] = epsCollection[indexEpsOpt]

                # Retrain model with optimal epsilon
                MODEL.setData(returnsAssets=assetsReturns[:trainingSize,:], returnsIndex=indexReturns[:trainingSize], beta=beta, rho=rho, alpha=alphaDaily)
                results_SAA_DRO = MODEL.solve(epsCollection=np.array([0, epsOpt[indexRho,TS,k]]), rhoCollection=np.array([rho]),
                                        betaCollection=betaCollection, progressBar=False);

                # Save portfolios
                wSAA = np.array(results_SAA_DRO.iloc[0,7:].values, dtype=np.float64)
                wDRO = np.array(results_SAA_DRO.iloc[1,7:].values, dtype=np.float64)

                # Test SAA portfolios on OoS
                MODEL.setOptimalPortfolio(wSAA)
                _, index_OoS, enhancedIndex_OoS, portfolioSAA_OoS = MODEL.testPortfolio(assetsReturns[trainingSize:,:],
                                                                                        indexReturns[trainingSize:], plot=False,
                                                                                        dataName="S&P500")

                # Test SAA portfolios on IS
                _, index_IS, enhancedIndex_IS, portfolioSAA_IS = MODEL.testPortfolio(assetsReturns[:trainingSize,:],
                                                                                        indexReturns[:trainingSize], plot=False,
                                                                                        dataName="S&P500")

                # Test DRO portfolio on OoS
                MODEL.setOptimalPortfolio(wDRO)
                _, _, _, portfolioDRO_OoS = MODEL.testPortfolio(assetsReturns[trainingSize:,:],
                                                                                        indexReturns[trainingSize:], plot=False,
                                                                                        dataName="S&P500")

                # Test DRO portfolio on IS
                _, _, _, portfolioDRO_IS = MODEL.testPortfolio(assetsReturns[:trainingSize,:],
                                                                                        indexReturns[:trainingSize], plot=False,
                                                                                        dataName="S&P500")

                # Save statistics
                PM.setData(portfolio=portfolioSAA_IS, index=index_IS, enhancedIndex=enhancedIndex_IS)
                metricsRecordings_SAA_IS = PM.getMetrics(rho=rho, beta=beta)

                # Compute metric for out-of-sample
                PM.setData(portfolio=portfolioSAA_OoS, index=index_OoS, enhancedIndex=enhancedIndex_OoS)
                metricsRecordings_SAA_OoS = PM.getMetrics(rho=rho, beta=beta)

                # Respectively calculate and log the performance in terms of the objective
                metricsRecordings_SAA_IS['Objective'] = results_SAA_DRO.iloc[0,0]
                metricsRecordings_SAA_OoS['Objective'] = MODEL.approximateObjective(assetsReturns[trainingSize:,:], indexReturns[trainingSize:], wSAA)

                # Save statistics
                PM.setData(portfolio=portfolioDRO_IS, index=index_IS, enhancedIndex=enhancedIndex_IS)
                metricsRecordings_DRO_IS = PM.getMetrics(rho=rho, beta=beta)

                # Compute metric for out-of-sample
                PM.setData(portfolio=portfolioDRO_OoS, index=index_OoS, enhancedIndex=enhancedIndex_OoS)
                metricsRecordings_DRO_OoS = PM.getMetrics(rho=rho, beta=beta)

                # Respectively calculate and log the performance in terms of the objective
                metricsRecordings_DRO_IS['Objective'] = results_SAA_DRO.iloc[1,0]
                metricsRecordings_DRO_OoS['Objective'] = MODEL.approximateObjective(assetsReturns[trainingSize:,:], indexReturns[trainingSize:], wDRO)

                # Prepare storage of all performance metrics
                for j, key in enumerate(metricsRecordings_SAA_IS):
                    IS_statistics[0,indexRho,TS,k,j] = metricsRecordings_SAA_IS[key]
                    IS_statistics[1,indexRho,TS,k,j] = metricsRecordings_DRO_IS[key]
                    OoS_statistics[0,indexRho,TS,k,j] = metricsRecordings_SAA_OoS[key]
                    OoS_statistics[1,indexRho,TS,k,j] = metricsRecordings_DRO_OoS[key]

                # Save trajectories
                if Tdx == 0:

                    index_OoS, enhancedIndex_OoS, portfolioSAA_OoS

                    # Save trajectories
                    increment = nextPeriodStartIndex - periodEndIndex + 1 # +1 because we want to include the first day of the next period
                    fromIndex = Tdx
                    toIndex = Tdx+increment

                    # Divide by 100 to make concatenation easier
                    trajectories[indexRho,TS,fromIndex:toIndex,0] = np.copy(index_OoS.flatten()/100)
                    trajectories[indexRho,TS,fromIndex:toIndex,1] = np.copy(enhancedIndex_OoS.flatten()/100)
                    trajectories[indexRho,TS,fromIndex:toIndex,2] = np.copy(portfolioSAA_OoS.flatten()/100)
                    trajectories[indexRho,TS,fromIndex:toIndex,3] = np.copy(portfolioDRO_OoS.flatten()/100)

                    # Overwrite with percentage changes instead
                    trajectories[indexRho,TS,fromIndex+1:toIndex,0] = np.diff(trajectories[indexRho,TS,fromIndex:toIndex,0])/trajectories[indexRho,TS,fromIndex:toIndex-1,0] + 1
                    trajectories[indexRho,TS,fromIndex+1:toIndex,1] = np.diff(trajectories[indexRho,TS,fromIndex:toIndex,1])/trajectories[indexRho,TS,fromIndex:toIndex-1,1] + 1
                    trajectories[indexRho,TS,fromIndex+1:toIndex,2] = np.diff(trajectories[indexRho,TS,fromIndex:toIndex,2])/trajectories[indexRho,TS,fromIndex:toIndex-1,2] + 1
                    trajectories[indexRho,TS,fromIndex+1:toIndex,3] = np.diff(trajectories[indexRho,TS,fromIndex:toIndex,3])/trajectories[indexRho,TS,fromIndex:toIndex-1,3] + 1

                    # Update Tdx
                    Tdx += increment

                else:

                    # Save trajectories
                    increment = nextPeriodStartIndex - periodEndIndex
                    fromIndex = Tdx
                    toIndex = Tdx+increment

                    # Normalize trajectories
                    indexNormalized = index_OoS.flatten()/100
                    enhancedIndexNormalized = enhancedIndex_OoS.flatten()/100
                    portfolioSAANormalized = portfolioSAA_OoS.flatten()/100
                    portfolioDRONormalized = portfolioDRO_OoS.flatten()/100

                    # Overwrite with percentage changes instead
                    trajectories[indexRho,TS,fromIndex:toIndex,0] = np.diff(indexNormalized)/indexNormalized[:-1] + 1
                    trajectories[indexRho,TS,fromIndex:toIndex,1] = np.diff(enhancedIndexNormalized)/enhancedIndexNormalized[:-1] + 1
                    trajectories[indexRho,TS,fromIndex:toIndex,2] = np.diff(portfolioSAANormalized)/portfolioSAANormalized[:-1] + 1
                    trajectories[indexRho,TS,fromIndex:toIndex,3] = np.diff(portfolioDRONormalized)/portfolioDRONormalized[:-1] + 1

                    # Update Tdx
                    Tdx += increment

                # Update progress bar
                pbar.update(1)

# ORDER
# ["Index", "Enhanced Index", "SAA", "DRO"]

# Save Wasserstein parameters
dataFrameTrajectoryDates = pd.DataFrame(allDates.values, columns=["Dates"])
dataFrameTrajectoryDates.to_csv("./Results/Backtest/RAERM/Frontier_TrajectoryDates.csv", index=False)

# Save Wasserstein parameters
dataFrameRebalanceDates = pd.DataFrame(rebalanceDates, columns=["Dates"])
dataFrameRebalanceDates.to_csv("./Results/Backtest/RAERM/Frontier_RebalanceDates.csv", index=False)

# Save core results to file with id

# Create logging string
line0 = "fileName: " + "Frontier_Backtest_RAERM_Trajectories" + "\n"
line1 = "alpha: {}".format(excessReturnAnually) + "\n"
line2 = "nEps: " + str(len(epsCollection)) + "\n"
line3 = "nBetas: " + str(len(betaCollection)) + "\n"
line4 = "nRhos: " + str(len(rhoCollection)) + "\n"
line5 = "epsCollection: " + "np.concatenate(([0], 10**np.linspace({}, {}, {})), axis=0)".format(startEps, endEps, totalEps) + "\n"
line6 = "betaCollection: " + ",".join([str(round(elem,5)) for elem in betaCollection]) + "\n"
line7 = "rhoCollection: " + ",".join([str(round(elem,5)) for elem in rhoCollection]) + "\n"
line8 = "trainingSize: " + "{}".format(trainingSize) + "\n"
line9 = "recover: " + ",".join([str(elem) for elem in trajectories.shape]) + "\n"
parameters = line0 + line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9

# Save results
write_parameters_to_file(trajectories.reshape(-1), parameters, file_name="Frontier_Backtest_RAERM_Trajectories", folder_path="./Results/Backtest/RAERM/", expId=1)

# Create logging string
line0 = "fileName: " + "Frontier_Backtest_RAERM_Wasserstein" + "\n"
line1 = "alpha: {}".format(excessReturnAnually) + "\n"
line2 = "nEps: " + str(len(epsCollection)) + "\n"
line3 = "nBetas: " + str(len(betaCollection)) + "\n"
line4 = "nRhos: " + str(len(rhoCollection)) + "\n"
line5 = "epsCollection: " + "np.concatenate(([0], 10**np.linspace({}, {}, {})), axis=0)".format(startEps, endEps, totalEps) + "\n"
line6 = "betaCollection: " + ",".join([str(round(elem,5)) for elem in betaCollection]) + "\n"
line7 = "rhoCollection: " + ",".join([str(round(elem,5)) for elem in rhoCollection]) + "\n"
line8 = "trainingSize: " + "{}".format(trainingSize) + "\n"
line9 = "recover: " + ",".join([str(elem) for elem in epsOpt.shape]) + "\n"
parameters = line0 + line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9

# Save results
write_parameters_to_file(epsOpt.reshape(-1), parameters, file_name="Frontier_Backtest_RAERM_epsOpt", folder_path="./Results/Backtest/RAERM/", expId=1)

# Create logging string
line0 = "fileName: " + "Frontier_Backtest_RAERM_trajectories" + "\n"
line1 = "alpha: {}".format(excessReturnAnually) + "\n"
line2 = "nEps: " + str(len(epsCollection)) + "\n"
line3 = "nBetas: " + str(len(betaCollection)) + "\n"
line4 = "nRhos: " + str(len(rhoCollection)) + "\n"
line5 = "epsCollection: " + "np.concatenate(([0], 10**np.linspace({}, {}, {})), axis=0)".format(startEps, endEps, totalEps) + "\n"
line6 = "betaCollection: " + ",".join([str(round(elem,5)) for elem in betaCollection]) + "\n"
line7 = "rhoCollection: " + ",".join([str(round(elem,5)) for elem in rhoCollection]) + "\n"
line8 = "trainingSize: " + "{}".format(trainingSize) + "\n"
line9 = "recover: " + ",".join([str(elem) for elem in trajectories.shape]) + "\n"
parameters = line0 + line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9

# Save results
write_parameters_to_file(trajectories.reshape(-1), parameters, file_name="Frontier_Backtest_RAERM_trajectories", folder_path="./Results/Backtest/RAERM/", expId=1)

# Save statistics

# Create logging string
line0 = "fileName: " + "Frontier_Backtest_RAERM_IS_statistics" + "\n"
line1 = "alpha: {}".format(excessReturnAnually) + "\n"
line2 = "nEps: " + str(len(epsCollection)) + "\n"
line3 = "nBetas: " + str(len(betaCollection)) + "\n"
line4 = "nRhos: " + str(len(rhoCollection)) + "\n"
line5 = "epsCollection: " + "np.concatenate(([0], 10**np.linspace({}, {}, {})), axis=0)".format(startEps, endEps, totalEps) + "\n"
line6 = "betaCollection: " + ",".join([str(round(elem,5)) for elem in betaCollection]) + "\n"
line7 = "rhoCollection: " + ",".join([str(round(elem,5)) for elem in rhoCollection]) + "\n"
line8 = "trainingSize: " + "{}".format(trainingSize) + "\n"
line9 = "recover: " + ",".join([str(elem) for elem in IS_statistics.shape]) + "\n"
parameters = line0 + line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9

# Save results
write_parameters_to_file(IS_statistics.reshape(-1), parameters, file_name="Frontier_Backtest_RAERM_IS_statistics", folder_path="./Results/Backtest/RAERM/", expId=1)

# Create logging string
line0 = "fileName: " + "Frontier_Backtest_RAERM_OoS_statistics" + "\n"
line1 = "alpha: {}".format(excessReturnAnually) + "\n"
line2 = "nEps: " + str(len(epsCollection)) + "\n"
line3 = "nBetas: " + str(len(betaCollection)) + "\n"
line4 = "nRhos: " + str(len(rhoCollection)) + "\n"
line5 = "epsCollection: " + "np.concatenate(([0], 10**np.linspace({}, {}, {})), axis=0)".format(startEps, endEps, totalEps) + "\n"
line6 = "betaCollection: " + ",".join([str(round(elem,5)) for elem in betaCollection]) + "\n"
line7 = "rhoCollection: " + ",".join([str(round(elem,5)) for elem in rhoCollection]) + "\n"
line8 = "trainingSize: " + "{}".format(trainingSize) + "\n"
line9 = "recover: " + ",".join([str(elem) for elem in OoS_statistics.shape]) + "\n"
parameters = line0 + line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9

# Save results
write_parameters_to_file(OoS_statistics.reshape(-1), parameters, file_name="Frontier_Backtest_RAERM_OoS_statistics", folder_path="./Results/Backtest/RAERM/", expId=1)