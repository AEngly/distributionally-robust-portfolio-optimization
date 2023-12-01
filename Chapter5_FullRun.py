"""
Author: Andreas Heidelbach Engly (s170303)
Purpose: This file generates the results for full comparison of models.

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
dataLoader = DataLoader(path='./Data/')
priceData = dataLoader.SP500(freq="daily", startDate="1999-01-01", intersect=False, filtered=True, endDate=dt.datetime.today().strftime("%Y-%m-%d"))
priceData['Dates'] = pd.to_datetime(priceData['Dates'])
totalObservations = priceData.shape[0]
priceDataIntersect = dataLoader.SP500(freq="daily", startDate="1999-01-01", intersect=True, filtered=True, endDate=dt.datetime.today().strftime("%Y-%m-%d"))
priceDataIntersect['Dates'] = pd.to_datetime(priceDataIntersect['Dates'])
totalObservationsIntersect = priceDataIntersect.shape[0]

#########################################################################################
#                             Control Experiment
#########################################################################################

# Specify central parameters
rho = 2
beta = 0.90
excessReturnAnually = 0
rfAnnualy = 0.02
alphaDaily = (1 + excessReturnAnually)**(1/252)-1
rfDaily = (1 + rfAnnualy)**(1/252)-1
rhoCollection=np.array([rho])
betaCollection=np.array([beta])

# Select range to search for optimal uncertainty
startEps = -8
endEps = 0
epsCollection = np.concatenate(([0], 10**np.linspace(startEps, endEps, 100)), axis=0)
totalEps = len(epsCollection)

# Specify training size
trainingSize = 252

# Specify size of validation set in percentage of trainingSize
validationPercentage = 0.20
validationSize = int(validationPercentage * trainingSize)

#########################################################################################
#                             Prepare rebalance dates
#########################################################################################

# Get all tickers
beginDate = pd.to_datetime("2001-01-01")
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
assetsReturns = priceData.iloc[:,2:].pct_change().dropna(axis=0).values

# Get returns for intersect
datesIntersect = priceDataIntersect.iloc[:,0]
indexIntersect = priceDataIntersect.iloc[:,1]
indexReturnsIntersect = priceDataIntersect.iloc[:,1].pct_change().dropna(axis=0).values
assetsIntersect = priceDataIntersect.iloc[:,2:]
assetsReturnsIntersect = priceDataIntersect.iloc[:,2:].pct_change().dropna(axis=0).values

# Allocate memory to save statistics
epsOpt = np.zeros(len(rebalanceIndices))

# Allocate space for portfolio values
totalDays = allDates.shape[0]
trajectories = np.zeros((totalDays,4))
Tdx = 0

# Initialize model and metrics engine
MODEL = ExcessCVaRModelDRO(beta=beta, rho=rho, alpha=alphaDaily, rf=rfDaily);
PM = PerformanceMetrics()

# Start the experiment. We do not include last rebalancing date as it defines the end of the experiment.
with tqdm(total=len(rebalanceIndices[:-1]), disable=False) as pbar:
    for k,idx in enumerate(rebalanceIndices[:-1]):

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
        MODEL.setData(returnsAssets=assetsReturns[:endTrainingIndex,:], returnsIndex=indexReturns[:endTrainingIndex], beta=beta, rho=rho, alpha=alphaDaily, rf=rfDaily)

        # Solve it for all epsilon
        results = MODEL.solve(epsCollection=epsCollection, rhoCollection=rhoCollection,
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
        epsOpt[k] = epsCollection[indexEpsOpt]

        # Retrain model with optimal epsilon
        MODEL.setData(returnsAssets=assetsReturns[:trainingSize,:], returnsIndex=indexReturns[:trainingSize], beta=beta, rho=rho, alpha=alphaDaily, rf=rfDaily)
        resultsDRO = MODEL.solve(epsCollection=np.array([epsOpt[k]]), rhoCollection=rhoCollection,
                                betaCollection=betaCollection, progressBar=False);

        # Save portfolios
        wSAA = np.array(results.iloc[0,7:].values, dtype=np.float64)
        wDRO = np.array(resultsDRO.iloc[0,7:].values, dtype=np.float64)

        # Test SAA portfolios
        MODEL.setOptimalPortfolio(wSAA)
        _, index, enhancedIndex, portfolioSAA = MODEL.testPortfolio(assetsReturns[trainingSize:,:],
                                                                                indexReturns[trainingSize:], plot=False,
                                                                                dataName="S&P500")

        # Test DRO portfolio
        MODEL.setOptimalPortfolio(wDRO)
        _, _, _, portfolioDRO = MODEL.testPortfolio(assetsReturns[trainingSize:,:],
                                                                                indexReturns[trainingSize:], plot=False,
                                                                                dataName="S&P500")

        if Tdx == 0:

            # Save trajectories
            increment = nextPeriodStartIndex - periodEndIndex + 1 # +1 because we want to include the first day of the next period
            fromIndex = Tdx
            toIndex = Tdx+increment

            # Divide by 100 to make concatenation easier
            trajectories[fromIndex:toIndex,0] = np.copy(index.flatten()/100)
            trajectories[fromIndex:toIndex,1] = np.copy(enhancedIndex.flatten()/100)
            trajectories[fromIndex:toIndex,2] = np.copy(portfolioSAA.flatten()/100)
            trajectories[fromIndex:toIndex,3] = np.copy(portfolioDRO.flatten()/100)

            # Overwrite with percentage changes instead
            trajectories[fromIndex+1:toIndex,0] = np.diff(trajectories[fromIndex:toIndex,0])/trajectories[fromIndex:toIndex-1,0] + 1
            trajectories[fromIndex+1:toIndex,1] = np.diff(trajectories[fromIndex:toIndex,1])/trajectories[fromIndex:toIndex-1,1] + 1
            trajectories[fromIndex+1:toIndex,2] = np.diff(trajectories[fromIndex:toIndex,2])/trajectories[fromIndex:toIndex-1,2] + 1
            trajectories[fromIndex+1:toIndex,3] = np.diff(trajectories[fromIndex:toIndex,3])/trajectories[fromIndex:toIndex-1,3] + 1

            # Update Tdx
            Tdx += increment

        else:

            # Save trajectories
            increment = nextPeriodStartIndex - periodEndIndex
            fromIndex = Tdx
            toIndex = Tdx+increment

            # Normalize trajectories
            indexNormalized = index.flatten()/100
            enhancedIndexNormalized = enhancedIndex.flatten()/100
            portfolioSAANormalized = portfolioSAA.flatten()/100
            portfolioDRONormalized = portfolioDRO.flatten()/100

            # Overwrite with percentage changes instead
            trajectories[fromIndex:toIndex,0] = np.diff(indexNormalized)/indexNormalized[:-1] + 1
            trajectories[fromIndex:toIndex,1] = np.diff(enhancedIndexNormalized)/enhancedIndexNormalized[:-1] + 1
            trajectories[fromIndex:toIndex,2] = np.diff(portfolioSAANormalized)/portfolioSAANormalized[:-1] + 1
            trajectories[fromIndex:toIndex,3] = np.diff(portfolioDRONormalized)/portfolioDRONormalized[:-1] + 1

            # Update Tdx
            Tdx += increment

        # Update progress bar
        pbar.update(1)

# Save results from portfolios
results = pd.DataFrame(trajectories, columns=["Index", "Enhanced Index", "SAA", "DRO"])
results['Dates'] = allDates.values
results.to_csv("./Results/Chapter5_FullRun/fullRunResults.csv", index=False)

# Save Wasserstein parameters
epsResults = pd.DataFrame(epsOpt, columns=["Epsilon"])
epsResults['Dates'] = rebalanceDates
epsResults.to_csv("./Results/Chapter5_FullRun/epsOpt.csv", index=False)

# Save core results to file with id

# Create logging string
line0 = "fileName: " + "ExcessModelDRO_trajectories" + "\n"
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
write_parameters_to_file(trajectories.reshape(-1), parameters, file_name="ExcessModelDRO_trajectories", folder_path="./Results/Chapter5_FullRun/", expId=1)

# Create logging string
line0 = "fileName: " + "ExcessModelDRO_epsOpt" + "\n"
line1 = "alpha: {}".format(excessReturnAnually) + "\n"
line2 = "nEps: " + str(len(epsCollection)) + "\n"
line3 = "nBetas: " + str(len(betaCollection)) + "\n"
line4 = "nRhos: " + str(len(rhoCollection)) + "\n"
line5 = "epsCollection: " + "np.concatenate(([0], 10**np.linspace({}, {}, {})), axis=0)".format(startEps, endEps, totalEps) + "\n"
line6 = "betaCollection: " + ",".join([str(round(elem,5)) for elem in betaCollection]) + "\n"
line7 = "rhoCollection: " + ",".join([str(round(elem,5)) for elem in rhoCollection]) + "\n"
line8 = "trainingSize: " + "{}".format(trainingSize) + "\n"
line9 = "length: " + "{}".format(len(epsOpt)) + "\n"
parameters = line0 + line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9

# Save results
write_parameters_to_file(epsOpt, parameters, file_name="ExcessModelDRO_epsOpt", folder_path="./Results/Chapter5_FullRun/", expId=1)
