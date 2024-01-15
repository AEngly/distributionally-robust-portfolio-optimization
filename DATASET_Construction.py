"""
Author: Andreas Heidelbach Engly (s170303)
Purpose: This script constructs datasets for evaluating models on S&P500 historical prices and constituent information. It includes scraping, modification of tickers, API requests to AlphaVantage for price data, downloading S&P500 index data from yfinance, and saving relevant data for later access by models.

Inputs:
- None

Outputs:
- Dataframes: historicalConstituents, completeDailySP500, completeWeeklySP500, contituents
- CSV files: HistoricalConstituents.csv, DailyHistoricalPrices.csv, WeeklyHistoricalPrices.csv, ConstituentInformation.csv

Dependencies:
- datetime, requests, BeautifulSoup, csv, pandas, numpy, yfinance, tqdm, re, pathlib, AlphaVantageFinance, DataLoader

Note: Ensure that the necessary AlphaVantage API key is available in the DataFetcher.py file.

# Section 1: Scraping
- Scrapes S&P500 constituents and changes from Wikipedia.
- Parses the data and handles missing dates.

# Section 2: Historical Constituents
- Constructs a dataset with historical constituents, considering changes over time.

# Section 3: Ticker Modifications
- Modifies tickers based on known changes and exclusions.

# Section 4: API request with 'AlphaVantage' to obtain data
- Creates an instance of AlphaVantageFinance class.
- Modifies tickers to fit the required format for the API.
- Fetches daily and weekly historical prices from AlphaVantage.

# Section 5: Download SP500 index data with yfinance
- Downloads daily and weekly S&P500 index data from yfinance.

# Section 6: Save relevant data for later access by models
- Saves constructed dataframes as CSV files in the specified data directory.

# Section 7: Creating a filtered data set with Data Loader
- Initializes DataLoader class.
- Saves raw and intersected datasets for daily and weekly frequencies.

# Exclude GICS sub-industries
- Filters tickers based on industry blacklist criteria.
- Creates filtered datasets for daily and weekly frequencies.

"""

# ## Dependencies

# Import necessary libraries
import datetime as dt
from datetime import datetime, timedelta, date
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import yfinance as yf
from pathlib import Path
from EITP.DataHandlers.DataFetcher import AlphaVantageFinance
from EITP.DataHandlers.DataLoader import DataLoader

# Print that script is starting
print("\n#########################################################################################\n")
print("                           Reconstructing the Dataset for S&P500                             ")
print("\n#########################################################################################\n")

# ## 1. Scraping

# Specify the range of interest
startingYear = 1999
startingMonth = 1
startingDay = 1
startingDate = date(startingYear, startingMonth, startingDay)
endDate = date.today()

# Specify the URL
URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
page = requests.get(URL)

# Print statement for Scraping section
print("Scraping completed successfully.")

# Parse the content
soup = BeautifulSoup(page.content, 'html.parser')

# Find tables in the content
tableConstituents = soup.find(id='constituents')
tableChanges = soup.find(id='changes')

# Specify column names for each table
columnNamesConstituents = [elem.text.strip() for elem in tableConstituents.find_all('th')]
columnNamesChanges = ['Date', 'AddedTicker', 'AddedSecurity', 'RemovedTicker', 'RemovedSecurity', 'Reason']

# Print statement for Parsing section
print("Parsing completed successfully.")

# Scrape rows from Constituents Table
rows = []
for row in tableConstituents.find_all('tr'):
    rowList = [elem.text.strip() for elem in row.find_all('td')]
    if rowList:
        rows.append(rowList)

contituents = pd.DataFrame(rows, columns=columnNamesConstituents)
contituents["Date added"] = pd.to_datetime(contituents["Date added"], format="%Y-%m-%d", errors='coerce')

# Print statement for Scraping Constituents section
print("Scraping Constituents completed successfully.")

# Scrape rows from Changes Table
rows = []
for row in tableChanges.find_all('tr'):
    rowList = [elem.text.strip() for elem in row.find_all('td')]
    if rowList:
        rows.append(rowList)

changes = pd.DataFrame(rows, columns=columnNamesChanges)
changes["Date"] = pd.to_datetime(changes["Date"], format="%B %d, %Y", errors='coerce')

# Print statement for Scraping Changes section
print("Scraping Changes completed successfully.")

# ## 2. Historical Constituents

# Define variables and add constituents today
tickers = contituents['Symbol'].to_list()
allRows = {'Date': [date.today().strftime('%Y-%m-%d')], 'Tickers': [','.join(tickers)], 'N': [len(tickers)]}
setTickers = set(tickers)
allTickers = set(tickers)

# Modify tickers according to changes
for DATE in np.flip(np.arange(startingDate, endDate, timedelta(days=1)).astype(datetime)):

    formattedDate = DATE.strftime("%Y-%m-%d")
    allRows['Date'].append(formattedDate)

    match = changes[changes['Date'] == formattedDate]

    if len(match) >= 1:
        addedTicker = list(match['AddedTicker'].values)
        addedTicker = set([ticker for ticker in addedTicker if ticker != ''])
        setTickers = setTickers.difference(addedTicker)

        removedTicker = list(match['RemovedTicker'].values)
        removedTicker = set([ticker for ticker in removedTicker if ticker != ''])
        setTickers = setTickers.union(removedTicker)
        allTickers = allTickers.union(removedTicker)

    allRows['Tickers'].append(','.join(list(setTickers)))
    allRows['N'].append(len(setTickers))

# Aggregate the data
allTickers = list(allTickers)
historicalConstituents = pd.DataFrame.from_dict(allRows)

# Print statement for Historical Constituents section
print("Historical Constituents construction completed successfully.")

# ## 3. Ticker Modifications

# Define dictionaries for ticker modifications
dailyNameChanges = ["ADS", "HFC", "NYX", "SMS", "FBHS", "GR", "HPH", "AV", "TRB", "ESV", "SBL", "ACE", "WIN", "CBE", "FNM", "QTRN", "FRE", "LEH", "NOVL", "BS", "GLK", "TYC", "WFR", "MEE", "DJ", "KSE", "CFC", "SLR", "RX", "CEPH", "FRC", "JCP", "TLAB", "ABK", "PTV", "EK", "ABS", "DF", "CCE", "SGP", "LDW", "GENZ", "MOLX", "BMC", "TE"]
weeklyNameChanges = ["JCP", "CFC", "CEPH", "NYX", "KSE", "NOVL", "SBL", "ABS", "FNM", "FRC", "ABK", "BS", "GLK", "TLAB", "HPH", "GR", "PTV", "LEH", "QTRN", "FBHS", "TYC", "AV", "MOLX", "ESV", "SGP", "MEE", "DJ", "SLR", "LDW", "HFC", "EK", "GENZ", "FRE", "ACE", "BMC", "CBE", "WFR", "RX", "TRB", "CCE", "WIN", "TE", "SMS", "DF"]

# Filter tickers based on modifications
filteredTickersDaily = [ticker for ticker in allTickers if ticker not in dailyNameChanges]
filteredTickersWeekly = [ticker for ticker in allTickers if ticker not in weeklyNameChanges]

# Print statement for Ticker Modifications section
print("Ticker Modifications completed successfully.")

# ## 4. Call AlphaVantage to Fetch Prices

# Create instances of the AlphaVantageFinance class
dailyFinanceAPI = AlphaVantageFinance()
weeklyFinanceAPI = AlphaVantageFinance()

# Modify tickers to fit the right format for the API
modifiedTickersDaily, _, _ = dailyFinanceAPI.modifyTickers(filteredTickersDaily, pattern=r'\b\w+\.\w+\b', replaceWith="-", replaceWhich=".")
modifiedTickersWeekly, _, _ = weeklyFinanceAPI.modifyTickers(filteredTickersWeekly, pattern=r'\b\w+\.\w+\b', replaceWith="-", replaceWhich=".")

# Fetch daily and weekly historical prices from AlphaVantage
print("Beginning download of stock prices ...")
aggregateDailySP500 = dailyFinanceAPI.returnPricesInterval(symbols=modifiedTickersDaily, function="DAILY_ADJUSTED", sampleType="5. adjusted close", redownload=True)
aggregateWeeklySP500 = weeklyFinanceAPI.returnPricesInterval(symbols=modifiedTickersWeekly, function="WEEKLY_ADJUSTED", sampleType="5. adjusted close", redownload=True)
print("Stock prices successfully downloaded.")

# ## 5. Download Historical Data for SP500

# Download daily data from yfinance
print("Beginning download of index prices ...")
dailySP500Index = yf.download(
    tickers = ["^GSPC"],
    start = min(aggregateDailySP500['Dates']),
    interval = "1d"
)['Adj Close']

dailySP500Index = pd.DataFrame({'Dates': dailySP500Index.index.values,'SPX-INDEX': dailySP500Index.values})

# Download weekly data from yfinance
weeklySP500Index = yf.download(
    tickers = ["^GSPC"],
    start = min(aggregateWeeklySP500['Dates']),
    interval = "1wk"
)['Adj Close']

weeklySP500 = pd.DataFrame({'Dates': weeklySP500Index.index.values,'SPX-INDEX': weeklySP500Index.values})
print("Index prices successfully downloaded.")

# Merge SPX index values with all assets
completeDailySP500 = pd.merge(dailySP500Index, aggregateDailySP500, on='Dates', how="right")
completeWeeklySP500 = pd.merge(dailySP500Index, aggregateWeeklySP500, on='Dates', how="right")

# Print statement for Downloading Historical Data section
print("Downloading Historical Data completed successfully.")

# ## 6. Save Constituents, GICS Categories and Historical Data to .csv

# Construct filepaths
filepath1 = Path('./Data/SP500/HistoricalConstituents.csv')
filepath2 = Path('./Data/SP500/DailyHistoricalPrices.csv')
filepath3 = Path('./Data/SP500/WeeklyHistoricalPrices.csv')
filepath4 = Path('./Data/SP500/ConstituentInformation.csv')

# Create necessary directories
filepath1.parent.mkdir(parents=True, exist_ok=True)

# Save dataframes as CSV files
historicalConstituents.to_csv(filepath1, index=False)
completeDailySP500.to_csv(filepath2, index=False)
completeWeeklySP500.to_csv(filepath3, index=False)
contituents.to_csv(filepath4, index=False)

# Print statement for Saving to CSV section
print("Data saved to CSV completed successfully.")

# ## 7. Creating a filtered data set with Data Loader

# Initialize the DataLoader class
DL = DataLoader(path='./Data/')

# Save SP500RawFull
dailySP500RawFull = DL.SP500(freq="daily", intersect=False, startDate=startingDate.strftime("%Y-%m-%d"), endDate=dt.datetime.today().strftime("%Y-%m-%d"))
dailyRawTickers = np.array(dailySP500RawFull.columns[2:], dtype=str)

weeklySP500RawFull = DL.SP500(freq="weekly", intersect=False, startDate=startingDate.strftime("%Y-%m-%d"), endDate=dt.datetime.today().strftime("%Y-%m-%d"))
weeklySP500RawFull = weeklySP500RawFull.loc[:, dailySP500RawFull.columns]
weeklyRawTickers = dailyRawTickers

# Construct filepaths
filepath1 = Path('./Data/SP500/dailySP500RawFull.csv')
filepath2 = Path('./Data/SP500/weeklySP500RawFull.csv')

# Create necessary directories
filepath1.parent.mkdir(parents=True, exist_ok=True)
filepath2.parent.mkdir(parents=True, exist_ok=True)

# Save dataframes as CSV files

# Create necessary directories
filepath1.parent.mkdir(parents=True, exist_ok=True)
filepath2.parent.mkdir(parents=True, exist_ok=True)

# Construct data sets
dailySP500RawFull.to_csv(filepath1, index=False)
weeklySP500RawFull.to_csv(filepath2, index=False)

# Load data from raw file
dailySP500RawIntersect = DL.SP500(freq="daily", intersect=True, startDate=startingDate.strftime("%Y-%m-%d"), endDate=dt.datetime.today().strftime("%Y-%m-%d"))
dailyIntersectTickers = np.array(dailySP500RawIntersect.columns[2:], dtype=str)

# Load data from raw file
weeklySP500RawIntersect = DL.SP500(freq="weekly", intersect=True, startDate=startingDate.strftime("%Y-%m-%d"), endDate=dt.datetime.today().strftime("%Y-%m-%d"))
weeklySP500RawIntersect = weeklySP500RawIntersect.loc[:, dailySP500RawIntersect.columns]
weeklyIntersectTickers = dailyIntersectTickers

# Construct filepaths
filepath1 = Path('./Data/SP500/dailySP500RawIntersect.csv')
filepath2 = Path('./Data/SP500/weeklySP500RawIntersect.csv')

# Create necessary directories
filepath1.parent.mkdir(parents=True, exist_ok=True)
filepath2.parent.mkdir(parents=True, exist_ok=True)

# Construct data sets
dailySP500RawIntersect.to_csv(filepath1, index=False)
weeklySP500RawIntersect.to_csv(filepath2, index=False)

# ## Exclude GICS sub-industries

industryMap = DL.filterIndustries()
blacklist = ['Aerospace & Defense',
             'Oil & Gas Equipment & Services'
             'Casinos & Gaming',
             'Integrated Oil & Gas',
             'Oil & Gas Exploration & Production',
             'Oil & Gas Refining & Marketing',
             'Tobacco',
             'Brewers',
             'Distillers & Vintners',
             'Oil & Gas Storage & Transportation']

# Start with raw
filteredTickersRaw = DL.filterTickers(dailyRawTickers, blacklist)

# .. then intersect
filteredTickersIntersect = DL.filterTickers(dailyIntersectTickers, blacklist)

# Start by creating it on raw
selector = list(dailySP500RawFull.columns[:2]) + filteredTickersRaw
dailySP500FilteredFull = dailySP500RawFull.loc[:,selector]
weeklySP500FilteredFull = weeklySP500RawFull.loc[:,selector]

# .. then create it on filtered
selector = list(dailySP500RawIntersect.columns[:2]) + filteredTickersIntersect
dailySP500FilteredIntersect = dailySP500RawIntersect.loc[:,selector]
weeklySP500FilteredIntersect = weeklySP500RawIntersect.loc[:,selector]

# Construct filepaths
filepath1 = Path('./Data/SP500/dailySP500FilteredFull.csv')
filepath2 = Path('./Data/SP500/weeklySP500FilteredFull.csv')
filepath3 = Path('./Data/SP500/dailySP500FilteredIntersect.csv')
filepath4 = Path('./Data/SP500/weeklySP500FilteredIntersect.csv')

# Create necessary directories
filepath1.parent.mkdir(parents=True, exist_ok=True)
filepath2.parent.mkdir(parents=True, exist_ok=True)
filepath3.parent.mkdir(parents=True, exist_ok=True)
filepath4.parent.mkdir(parents=True, exist_ok=True)

# Construct data sets
dailySP500FilteredFull.to_csv(filepath1, index=False)
weeklySP500FilteredFull.to_csv(filepath2, index=False)
dailySP500FilteredIntersect.to_csv(filepath3, index=False)
weeklySP500FilteredIntersect.to_csv(filepath4, index=False)

# Print that script finished successfully
print("\n#########################################################################################\n")
print("                           Status: Completed successfully!                                   ")
print("\n#########################################################################################\n")

