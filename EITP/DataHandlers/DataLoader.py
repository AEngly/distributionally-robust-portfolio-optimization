"""
Author: Andreas Heidelbach Engly (s170303)
Purpose: This script provides a data loading and filtering utility class for SP500 historical prices and constituent information.
         It allows for extracting daily or weekly data within specified date ranges, filtering based on available tickers, and handling sector and industry information.

Completion time: Approximately 30 minutes

Inputs:
- Path to the data directory (default: './Data/')
- Frequency ('daily' or 'weekly')
- Start and end dates for filtering

Outputs:
- Filtered historical prices dataset ('pricesSP500') based on the specified criteria

Dependencies:
- sys, os, re, glob, datetime, numpy, pandas, matplotlib, mosek.fusion, tqdm, scipy.stats

Class Methods:
- SP500: Extracts SP500 historical prices based on specified parameters.
- FilteredSP500: Extracts filtered SP500 historical prices using pre-filtered constituent information.
- filterSectors: Creates a map of tickers to their corresponding GICS sectors.
- filterIndustries: Creates a map of tickers to their corresponding GICS sub-industries.
- filterTickers: Filters tickers based on industry blacklist criteria.

Note: Ensure that the necessary CSV files (ConstituentInformation.csv, HistoricalConstituents.csv, DailyHistoricalPrices.csv, WeeklyHistoricalPrices.csv)
      are available in the specified data directory.
"""

# Dependencies
import re
import datetime as dt
import pandas as pd
from mosek.fusion import *

# Class definition
class DataLoader:

    def __init__(self, path='./Data/'):

        self.dataPath = path;
        self.historicalConstituents = pd.read_csv("{}SP500/HistoricalConstituents.csv".format(self.dataPath));

    def SP500(self, freq="daily", intersect=True, filtered=False, startDate="2012-01-01", endDate=dt.datetime.today().strftime("%Y-%m-%d")):

        if filtered:
            # Load raw files (path is relative to the file used to call the library)
            historicalConstituents = self.historicalConstituents
            dailySP500 = pd.read_csv("{}SP500/dailySP500FilteredFull.csv".format(self.dataPath));
            weeklySP500 = pd.read_csv("{}SP500/weeklySP500FilteredFull.csv".format(self.dataPath));
        else:
            # Load raw files (path is relative to the file used to call the library)
            historicalConstituents = self.historicalConstituents
            dailySP500 = pd.read_csv("{}SP500/dailySP500RawFull.csv".format(self.dataPath));
            weeklySP500 = pd.read_csv("{}SP500/weeklySP500RawFull.csv".format(self.dataPath));

        # Filter based on dates

        # 1) Constituents
        constituents = historicalConstituents[historicalConstituents['Date'] >= startDate]
        constituents = constituents[constituents['Date'] <= endDate]

        # 2) Include only tickers that have been present throughout the entire period
        if intersect:
            P1 = len(constituents['Tickers'])
            tickers = set(constituents['Tickers'].iloc[0].split(","))
            for i in range(1, P1):
                iterativeTickers = set(constituents['Tickers'].iloc[i].split(","))
                tickers = tickers.intersection(iterativeTickers)
        else:
            P1 = len(constituents['Tickers'])
            tickers = set(constituents['Tickers'].iloc[0].split(","))
            for i in range(1, P1):
                iterativeTickers = set(constituents['Tickers'].iloc[i].split(","))
                tickers = tickers.union(iterativeTickers)

        # 3) Replace "." with "-"
        text = " ".join(tickers)
        matches = re.findall(r'\b\w+\.\w+\b', text)
        replacements = [ticker.replace(".", "-") for ticker in matches]
        tickers = tickers.difference(matches)
        tickers = tickers.union(replacements)

        # 4) Filter prices on same dates
        if freq == "daily":

            # Filter rows based on date range
            pricesSP500 = dailySP500[(dailySP500['Dates'] >= startDate) & (dailySP500['Dates'] <= endDate)]

            # Extract relevant tickers
            allTickers = pricesSP500.columns[2:]
            selectedTickers = list(allTickers[allTickers.isin(tickers)])

            # Remove rows where fewer than 10 values are non-NaN
            pricesSP500 = pricesSP500.dropna(subset=selectedTickers + ['Dates', 'SPX-INDEX'], thresh=10)

            # Select columns of interest and drop NaN columns (only if intersect = False)
            if intersect:
                pricesSP500 = pricesSP500[['Dates', 'SPX-INDEX'] + selectedTickers].dropna(axis='columns', how='any')
            else:
                pricesSP500 = pricesSP500[['Dates', 'SPX-INDEX'] + selectedTickers]

            # Reset the index
            pricesSP500 = pricesSP500.reset_index(drop=True)

        elif freq == "weekly":

           # Filter rows based on date range
            pricesSP500 = weeklySP500[(weeklySP500['Dates'] >= startDate) & (weeklySP500['Dates'] <= endDate)]

            # Extract relevant tickers
            allTickers = pricesSP500.columns[2:]
            selectedTickers = list(allTickers[allTickers.isin(tickers)])

            # Remove rows where fewer than 10 values are non-NaN
            pricesSP500 = pricesSP500.dropna(subset=selectedTickers + ['Dates', 'SPX-INDEX'], thresh=10)

            # Select columns of interest and drop NaN columns (only if intersect = False)
            if intersect:
                pricesSP500 = pricesSP500[['Dates', 'SPX-INDEX'] + selectedTickers].dropna(axis='columns', how='any')
            else:
                pricesSP500 = pricesSP500[['Dates', 'SPX-INDEX'] + selectedTickers]

            # Reset the index
            pricesSP500 = pricesSP500.reset_index(drop=True)

        # Return the filtered dataset
        return pricesSP500

    def InterestRates(self, maturity="3 Mo", dailyRate=True, startDate="2012-01-01", endDate=dt.datetime.today().strftime("%Y-%m-%d")):

        # Load yields from CSV
        rates = pd.read_csv("{}InterestRates/yield-curve-rates-1990-2023.csv".format(self.dataPath));
        rates = rates[(rates['Dates'] >= startDate) & (rates['Dates'] <= endDate)]

        # Return the filtered dataset
        return rates[['Dates', maturity]].sort_values(by=['Dates']).reset_index(drop=True)

    def AggregateData(self, intersect=True, filtered=False, startDate="2012-01-01", endDate=dt.datetime.today().strftime("%Y-%m-%d")):

        if filtered and intersect:
            allData = pd.read_csv("{}Combined/dailyReturnsFilteredIntersect.csv".format(self.dataPath));
        elif filtered and not intersect:
            allData = pd.read_csv("{}Combined/dailyPricesFilteredIntersect.csv".format(self.dataPath));
        elif not filtered and intersect:
            allData = pd.read_csv("{}Combined/dailyReturnsIntersect.csv".format(self.dataPath));
        elif not filtered and not intersect:
            allData = pd.read_csv("{}Combined/dailyPricesFull.csv".format(self.dataPath));
        else:
            print("Something went wrong. Check the source code.")

        # The filter based on the selected dates
        allData[(allData['Dates'] >= startDate) & (allData['Dates'] <= endDate)]

        # Return the dataset
        return allData

    def filterSectors(self):

        # Load information table
        informationTable = pd.read_csv('{}SP500/ConstituentInformation.csv'.format(self.dataPath))

        # Create a map
        sectorMap = dict()
        sectors = informationTable['GICS Sector'].values
        for idx, ticker in enumerate(informationTable['Symbol'].values):
            modifiedTicker = ticker.replace(".", "-")
            sectorMap[modifiedTicker] = sectors[idx]

        return sectorMap

    def filterIndustries(self):

        # Load information table
        informationTable = pd.read_csv('{}SP500/ConstituentInformation.csv'.format(self.dataPath))

        # Create a map
        industryMap = dict()
        subIndustries = informationTable['GICS Sub-Industry'].values
        for idx, ticker in enumerate(informationTable['Symbol'].values):
            modifiedTicker = ticker.replace(".", "-")
            industryMap[modifiedTicker] = subIndustries[idx]

        return industryMap

    def filterTickers(self, tickers, blacklist):

        # Create list to save results
        filteredTickers = []

        # Create industry map
        industryMap = self.filterIndustries()

        # Loop over all included tickers
        for ticker in tickers:

            # Add tickers if not blacklisted
            if ticker in industryMap and industryMap[ticker] not in blacklist:
                filteredTickers.append(ticker)

            # If ticker not in industry map, add it anyway as we do not know the industry
            if ticker not in industryMap:
                filteredTickers.append(ticker)

        # Return the filtered tickers
        return filteredTickers

    def getTickerRange(self, startDate="1999-01-01", endDate="2023-20-11"):

        # Start by selecting the data range
        constituents = self.historicalConstituents
        filteredConstituents = constituents[constituents['Date'] >= startDate]
        filteredConstituents = filteredConstituents[filteredConstituents['Date'] <= endDate]

        # Then compute the intersection
        P1 = len(filteredConstituents['Tickers'])
        tickers = set(constituents['Tickers'].iloc[0].split(","))
        for i in range(1, P1):
            iterativeTickers = set(constituents['Tickers'].iloc[i].split(","))
            tickers = tickers.intersection(iterativeTickers)

        # Return the tickers
        return list(tickers)








