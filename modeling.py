import numpy as np
import pandas as pd
import statsmodels
import statsmodels.formula.api as smf
import statsmodels.api as sm
import statsmodels.tsa as ts
import yfinance as yf

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
        print(ts.stattools.coint(self.csv[ticker1],self.csv[ticker2]))



data = Model("historical-data.csv")
data.correlation()


print(data.cointergration("AAPL", "ATLC"))
