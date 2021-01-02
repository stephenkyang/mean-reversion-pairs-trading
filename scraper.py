import numpy as np
import pandas as pd
import statsmodels
import statsmodels.formula.api as smf
import statsmodels.api as sm
import statsmodels.tsa as ts
import yfinance as yf

class yFinanceScraper(object):
    namelist = []
    first = True
    df = None
    def __init__(self,names):
        self.names = names
        self.historicallist= []
        for name in self.names:
            self.namelist.append(name)
            ticker = yf.Ticker(name)
            data = ticker.history(period="1y").loc[: , ["Close"]]
            data = data.rename(columns={"Date": "Date", "Close": name})
            if self.first:
                self.df = data
                self.first = False
            else:
                self.df = self.df.join(data)


data = pd.read_csv("/Users/stephen/Desktop/Pairs Trading Project/ticker-names-on-NASDAQ-NYSE.csv")
data = data[data["Volume"] > 10000][data["IPO Year"] < 2010][data["Symbol"] != "AMHC"]["Symbol"]

#for storing testing data
scraper = yFinanceScraper(data)
for ticker in scraper.df:
    normalized_ticker_data = (scraper.df[ticker]-scraper.df[ticker].min())/(scraper.df[ticker].max()-scraper.df[ticker].min())
    scraper.df[ticker] = normalized_ticker_data

scraper.df.to_csv("historical-data.csv")