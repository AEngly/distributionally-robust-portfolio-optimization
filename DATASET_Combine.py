"""
Author: Andreas Heidelbach Engly (s170303)
Date: 15-01-2024
Description: This file combines the fetched data, structure it to make the rest of the operations easy, and then save the new format as files.

Dependencies:
- See below.

Usage:
- Change "startDate" to the first one to include in the files.

Note:
- No additional notes.

"""

# Print that script is starting
print("\n#########################################################################################\n")
print("                           Combining Sources to Dataset for S&P500                           ")
print("\n#########################################################################################\n")

# Specify first date to include in the dataset
startDate = "1999-01-01"

# Load dependencies
import datetime as dt
import numpy as np
import pandas as pd
from mosek.fusion import *
from sys import getsizeof
from pathlib import Path

# Imports from module
from EITP.DataHandlers.DataLoader import DataLoader;

# MAKE A FILE OF RETURNS WITH ALL CONSTITUENTS THAT HAVE BEEN PRESENT IN THE ENTIRE PERIOD

# Start by instantiating the data loader
dataLoader = DataLoader(path='./Data/');
priceData = dataLoader.SP500(freq="daily", filtered=False, intersect=True, startDate=startDate, endDate=dt.datetime.today().strftime("%Y-%m-%d"));
yieldData = dataLoader.InterestRates(maturity="3 Mo", startDate=startDate, endDate=dt.datetime.today().strftime("%Y-%m-%d"))
totalObservations = priceData.shape[0]

# Convert to daily yields (only works for 3 Mo)
yieldData["3 Mo"] = (1 + yieldData['3 Mo']/100)**(1/252) - 1
yieldData = yieldData.dropna(axis=0)

# Get asset data
aggregateData = pd.merge(yieldData, priceData, on='Dates', how='inner')

# Format the output
dates = aggregateData['Dates']
index = aggregateData['SPX-INDEX']
indexReturns = np.array([None] + list(index.pct_change().dropna(axis=0)))
equity = aggregateData.drop(labels=['Dates', '3 Mo', 'SPX-INDEX'], axis=1)
equityReturns = equity.pct_change().dropna(axis=0)
treasuryReturns = aggregateData['3 Mo'].values[:-1].reshape(-1,1)
assetReturns = np.concatenate([treasuryReturns, equityReturns], axis=1)

# Add row of None to assetReturns
noneArray = np.array([None for i in range(assetReturns.shape[1])])
assetReturns = np.concatenate([noneArray.reshape(1,-1), assetReturns], axis=0)

# Save the data to avoid further mistakes
allReturns = pd.DataFrame(assetReturns)
allReturns.insert(0, 'Dates', dates)
allReturns.insert(1, 'SPX-INDEX', indexReturns)
allReturns = allReturns.rename(columns={0: 'TREASURY-3M'})
allReturns = allReturns.dropna(axis=0)

# Save file
filepath = Path('./Data/Combined/dailyReturnsIntersect.csv')
allReturns.to_csv(filepath, index=False)

# MAKE A FILE OF PRICES AND YIELDS WITH ALL HISTORICAL CONSTITUENTS

# Start by instantiating the data loader
dataLoader = DataLoader(path='./Data/');
priceData = dataLoader.SP500(freq="daily", filtered=False, intersect=False, startDate=startDate, endDate=dt.datetime.today().strftime("%Y-%m-%d"));
yieldData = dataLoader.InterestRates(maturity="3 Mo", startDate=startDate, endDate=dt.datetime.today().strftime("%Y-%m-%d"))
totalObservations = priceData.shape[0]

# Convert to daily yields (only works for 3 Mo)
yieldData["3 Mo"] = (1 + yieldData['3 Mo']/100)**(1/252) - 1
yieldData = yieldData.dropna(axis=0)

# Get asset data
aggregateData = pd.merge(yieldData, priceData, on='Dates', how='inner')
aggregateData = aggregateData.rename(columns={'3 Mo': 'TREASURY-3M'})

# Get dates and index
dates = aggregateData['Dates']
index = aggregateData['SPX-INDEX']

# Reorder to dates, index, cash return, equity
aggregateData = aggregateData.drop(labels=['Dates', 'SPX-INDEX'], axis=1)

# Insert dates and index in the right order
aggregateData.insert(0, 'Dates', dates)
aggregateData.insert(1, 'SPX-INDEX', index)

# Save file
filepath = Path('./Data/Combined/dailyPricesFull.csv')
aggregateData.to_csv(filepath, index=False)

# MAKE A FILE OF RETURNS WITH ALL CONSTITUENTS THAT HAVE BEEN PRESENT IN THE ENTIRE PERIOD EXCLUDING BLACKLIST

# Start by instantiating the data loader
dataLoader = DataLoader(path='./Data/');
priceData = dataLoader.SP500(freq="daily", filtered=True, intersect=True, startDate=startDate, endDate=dt.datetime.today().strftime("%Y-%m-%d"));
yieldData = dataLoader.InterestRates(maturity="3 Mo", startDate=startDate, endDate=dt.datetime.today().strftime("%Y-%m-%d"))
totalObservations = priceData.shape[0]

# Convert to daily yields (only works for 3 Mo)
yieldData["3 Mo"] = (1 + yieldData['3 Mo']/100)**(1/252) - 1
yieldData = yieldData.dropna(axis=0)

# Get asset data
aggregateData = pd.merge(yieldData, priceData, on='Dates', how='inner')

# Format the output
dates = aggregateData['Dates']
index = aggregateData['SPX-INDEX']
indexReturns = np.array([None] + list(index.pct_change().dropna(axis=0)))
equity = aggregateData.drop(labels=['Dates', '3 Mo', 'SPX-INDEX'], axis=1)
equityReturns = equity.pct_change().dropna(axis=0)
treasuryReturns = aggregateData['3 Mo'].values[:-1].reshape(-1,1)
assetReturns = np.concatenate([treasuryReturns, equityReturns], axis=1)

# Add row of None to assetReturns
noneArray = np.array([None for i in range(assetReturns.shape[1])])
assetReturns = np.concatenate([noneArray.reshape(1,-1), assetReturns], axis=0)

# Save the data to avoid further mistakes
allReturns = pd.DataFrame(assetReturns)
allReturns.insert(0, 'Dates', dates)
allReturns.insert(1, 'SPX-INDEX', indexReturns)
allReturns = allReturns.rename(columns={0: 'TREASURY-3M'})

# Save file
filepath = Path('./Data/Combined/dailyReturnsFilteredIntersect.csv')
allReturns.to_csv(filepath, index=False)

# MAKE A FILE OF PRICES AND YIELDS WITH ALL HISTORICAL CONSTITUENTS EXCLUDING BLACKLIST

# Start by instantiating the data loader
dataLoader = DataLoader(path='./Data/');
priceData = dataLoader.SP500(freq="daily", filtered=True, intersect=False, startDate=startDate, endDate=dt.datetime.today().strftime("%Y-%m-%d"));
yieldData = dataLoader.InterestRates(maturity="3 Mo", startDate=startDate, endDate=dt.datetime.today().strftime("%Y-%m-%d"))
totalObservations = priceData.shape[0]

# Convert to daily yields (only works for 3 Mo)
yieldData["3 Mo"] = (1 + yieldData['3 Mo']/100)**(1/252) - 1
yieldData = yieldData.dropna(axis=0)

# Get asset data
aggregateData = pd.merge(yieldData, priceData, on='Dates', how='inner')
aggregateData = aggregateData.rename(columns={'3 Mo': 'TREASURY-3M'})

# Get dates and index
dates = aggregateData['Dates']
index = aggregateData['SPX-INDEX']

# Reorder to dates, index, cash return, equity
aggregateData = aggregateData.drop(labels=['Dates', 'SPX-INDEX'], axis=1)

# Insert dates and index in the right order
aggregateData.insert(0, 'Dates', dates)
aggregateData.insert(1, 'SPX-INDEX', index)

# Save file
filepath = Path('./Data/Combined/dailyPricesFilteredFull.csv')
aggregateData.to_csv(filepath, index=False)