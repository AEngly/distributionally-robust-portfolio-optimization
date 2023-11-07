"""
Author: Andreas Heidelbach Engly (s170303)
Purpose: [Briefly describe the purpose of the script or program]

Inputs:
- [List the input parameters, data sources, or any relevant information]

Outputs:
- [List the expected output, results, or any relevant information]
"""

# Dependencies
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

# Class definition
class DataLoader:

    def __init__(self, path='./Data/'):

        self.dataPath = path;

    def SP500(self, freq="daily", startDate="2012-01-01", endDate=dt.datetime.today().strftime("%Y-%m-%d")):

        # Load raw files
        historicalConstituents = pd.read_csv("{}SP500/HistoricalConstituents.csv".format(self.dataPath));
        dailySP500 = pd.read_csv("{}SP500/DailyHistoricalPrices.csv".format(self.dataPath));
        weeklySP500 = pd.read_csv("{}SP500/WeeklyHistoricalPrices.csv".format(self.dataPath));

        # Filter based on dates

        # 1) Constituents
        constituents = historicalConstituents[historicalConstituents['Date'] >= startDate]
        constituents = constituents[constituents['Date'] < endDate]

        # 2) Include only tickers that have been present throughout the entire period
        P1 = len(constituents['Tickers'])
        tickers = set(constituents['Tickers'].iloc[0].split(","))
        for i in range(1, P1):
            iterativeTickers = set(constituents['Tickers'].iloc[i].split(","))
            tickers = tickers.intersection(iterativeTickers)

        # 3) Replace "." with "-"
        text = " ".join(tickers)
        matches = re.findall(r'\b\w+\.\w+\b', text)
        replacements = [ticker.replace(".", "-") for ticker in matches]
        tickers = tickers.difference(matches)
        tickers = tickers.union(replacements)

        # 4) Filter prices on same dates
        if freq == "daily":
            pricesSP500 = dailySP500[dailySP500['Dates'] >= startDate]
            pricesSP500 = pricesSP500[pricesSP500['Dates'] < endDate]
            allTickers = pricesSP500.columns[2:]
            selectedTickers = list(allTickers[allTickers.isin(tickers)])
            pricesSP500 = pricesSP500[['Dates', 'SPX-INDEX'] + selectedTickers]
            pricesSP500 = pricesSP500.dropna(axis='columns', how='any')
            pricesSP500 = pricesSP500.reset_index(drop=True)

        elif freq == "weekly":
            pricesSP500 = dailySP500[weeklySP500['Dates'] >= startDate]
            pricesSP500 = pricesSP500[pricesSP500['Dates'] < endDate]
            allTickers = pricesSP500.columns[2:]
            selectedTickers = list(allTickers[allTickers.isin(tickers)])
            pricesSP500 = pricesSP500[['Dates', 'SPX-INDEX'] + selectedTickers]
            pricesSP500 = pricesSP500.dropna(axis='columns', how='any')
            pricesSP500 = pricesSP500.reset_index(drop=True)

        # Return the filtered dataset
        return pricesSP500;






