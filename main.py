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
scraper.df.to_csv("historical-data.csv")
#for real time use

class Model(object):
    def __init__(self, csv):
        self.csv = pd.read_csv(csv)
        self.corr_mat = None
        self.coint_mat = None #potentially there if you find out how to utilize johansen test for coint
        self.hedge_ratio = None #for coint
    def correlation(self):
        self.corr_mat = self.csv.corr()
        for x in data.corr_mat:
            data.corr_mat[x][x]=0
        return self.corr_mat
    def cointergration(self, ticker1, ticker2):
        return ts.stattools.coint(self.csv[ticker1],self.csv[ticker2])


data = Model("historical-data.csv")
data.correlation()
print(data.cointergration("AAPL", "ATLC"))
