# Dependencies
from datetime import datetime, date
import requests
import pandas as pd
import numpy as np
from tqdm import tqdm
import re

# Definition of class
class AlphaVantageFinance:

    def __init__(self, API_KEY="0Y981SYNSMU72WEL"):

        # Get API-key here: https://www.alphavantage.co/support/#api-key
        self.API_KEY = API_KEY

        # Placeholder for latest download
        self.latestDownload = None
        self.latestErrors = []

        # Error in downloads
        self.errors = 0

    def downloadPrices(self, symbol="IBM", function="DAILY_ADJUSTED", outputSize="full", sampleTypes=["5. adjusted close"]):

        # Description:
        # Purpose: Function is used to download historical prices
        data = {}

        # Specify call on specific ticker
        try:
            if function == "DAILY_ADJUSTED":
                incompleteURL = 'https://www.alphavantage.co/query?function=TIME_SERIES_{}&outputsize={}&symbol={}&apikey={}'
                URL = incompleteURL.format(function, outputSize, symbol, self.API_KEY)
                r = requests.get(URL)
                data = r.json()['Time Series (Daily)']

            elif function == "WEEKLY_ADJUSTED":
                incompleteURL = 'https://www.alphavantage.co/query?function=TIME_SERIES_{}&symbol={}&apikey={}'
                URL = incompleteURL.format(function, symbol, self.API_KEY)
                r = requests.get(URL)
                data = r.json()['Weekly Adjusted Time Series']

            elif function == "MONTHLY_ADJUSTED":
                incompleteURL = 'https://www.alphavantage.co/query?function=TIME_SERIES_{}&symbol={}&apikey={}'
                URL = incompleteURL.format(function, symbol, self.API_KEY)
                r = requests.get(URL)
                data = r.json()['Time Series (Monthly)']

            else:
                print("The variable 'dataType' did not match. See documentation.")

        except KeyError:
            self.errors += 1
            self.latestErrors.append(symbol)
            #print("Error {} occured for the following ticker: {}".format(self.errors, symbol))


        # Total samples
        N = len(data)
        M = len(sampleTypes)

        # Allocate memory
        levels = np.zeros((N,M))
        dates = np.zeros(N, dtype='datetime64[s]')

        # Destructure JSON object
        for idx, key in enumerate(data):
            for jdx, sampleType in enumerate(sampleTypes):
                levels[idx, jdx] = data[key][sampleType]

            # Save date
            timeComponents = [int(string) for string in key.split("-")]
            year = timeComponents[0]
            month = timeComponents[1]
            day = timeComponents[2]
            dates[idx] = date(year, month, day)

        # Then we can build a Pandas dataframe
        df = pd.DataFrame()
        df['Dates'] = dates

        # Save all the prices
        for jdx, sampleType in enumerate(sampleTypes):
            df[sampleType] = levels[:, jdx]

        # Set latest download
        self.latestDownload = df

        # Return the data
        return df

    def searchTicker(self, keyword="microsoft"):

        incompleteURL = 'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={}&apikey={}'
        URL = incompleteURL.format(keyword, self.API_KEY)
        r = requests.get(URL)
        matches = r.json()['bestMatches']
        df = pd.DataFrame.from_dict(matches)
        return df

    def downloadManyPrices(self, symbols=["IBM", "MSTF"], function="DAILY_ADJUSTED", outputSize="full", sampleType="5. adjusted close"):

        # Description:
        # Purpose: Function is used to download historical prices for a list of tickers

        # Setup for download bar
        with tqdm(total=len(symbols)) as pbar:

            # Download data on first ticker
            data = self.downloadPrices(symbol=symbols[0], function=function, sampleTypes=[sampleType])
            data = data.rename(columns={sampleType: symbols[0]})
            pbar.update(1)

            # Download data on all the other tickers
            for symbol in symbols[1:]:

                # Download symbol/ticker data
                df = self.downloadPrices(symbol=symbol, function=function, sampleTypes=[sampleType])
                df = df.rename(columns={sampleType: symbol})

                # Join the dataframe with the exisiting one
                data = pd.merge(data, df, on='Dates', how="outer")

                # Increment download bar
                pbar.update(1)

        # Cast date column into datetime
        data["Dates"] = pd.to_datetime(data["Dates"], format="%Y-%m-%d", errors='coerce')

        # Return the data
        return data

    def returnPricesInterval(self, startDate = '1900-1-1', endDate = datetime.today(), symbols=["IBM"], function="DAILY_ADJUSTED", sampleType="5. adjusted close", redownload=False):

        # Start download if not already done
        if redownload or self.latestDownload is None:
            self.latestDownload = self.downloadManyPrices(symbols=symbols, function=function, sampleType=sampleType)

        # Then return the appropriate range
        data = self.latestDownload[self.latestDownload['Dates'] >= startDate]
        data = data[data['Dates'] <= endDate]

        # Sort data
        data = data.sort_values(by="Dates")

        # Then return the data
        return data

    def downloadFundamentals(self, symbol="IBM", function="BALANCE_SHEET", reports="annualReports", filters=["hej"]):

        # Description
        # Purpose: Function is used to download historical balance sheets

        # Specify call on specific ticker
        if function == "BALANCE_SHEET":
            incompleteURL = 'https://www.alphavantage.co/query?function={}&symbol={}&apikey={}'
            URL = incompleteURL.format(function, symbol, self.API_KEY)
            r = requests.get(URL)
            data = r.json()[reports]
        else:
            print("The variable 'dataType' did not match. See documentation.")

        # Total reports and filter length
        N = len(data)
        F = len(filters)

        # Allocate memory
        np.zeros((N+1,F))

        # Test
        df = pd.DataFrame([data[0]])

        return data

    def modifyTickers(self, tickers, pattern=r'\b\w+\.\w+\b', replaceWith="-", replaceWhich="."):

        # Join all list elements
        text = " ".join(tickers)

        # Search for strings with dot
        matches = re.findall(pattern, text)

        # Modify the matches
        modifiedMatches = [string.replace(replaceWhich, replaceWith) for string in matches]
        modifiedMatchesCopy = modifiedMatches.copy()

        # Remove the matches and add the modified ones
        for match in matches:
            tickers.remove(match)
            tickers.append(modifiedMatches.pop())

        # Return all matches
        return tickers, matches, modifiedMatchesCopy
