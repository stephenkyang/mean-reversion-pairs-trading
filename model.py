import numpy as np
import pandas as pd
import statsmodels
from statsmodels.tsa.stattools import adfuller as adf
from sklearn import linear_model
import matplotlib.pyplot as plt
import matplotlib
from sklearn import preprocessing


data = pd.read_csv("historical-data.csv")
data = data[data.columns[:100]]

# 1. Do the necessary regression models to find cointegrating pairs, whether that be ADF, EGranger, or Johaness
# 2. Find pairs with wide spreads, through the calculation of stockA-stockB*(beta of regressive analysis)
# 3. Output certain pairs that are cointergrated/correlated
# 4. (Optional) Build a simple GUI that helps visualize the cointegration/spreads
# 5. (Optional) Make it live?

def correlation(data):
    corr_mat = data.corr()
    for x in corr_mat:
        corr_mat[x][x]=0
    return corr_mat

#EGranger test
def cointergration_test(ticker1, ticker2):
    return statsmodels.tsa.stattools.coint(data[ticker1],data[ticker2])

#will complete later as it is comparable to the EGranger test
def ADF(ticker1, ticker2):
    return

correlation_matrix = correlation(data)
cointegrated_pairs = {}

correlation_matrix = correlation(data)
correlated_pairs = {}
cointegrated_pairs = {}

def finding_correlated_pairs(correlation_matrix, threshold =.75):
    for ticker in correlation_matrix:
        for other_ticker, value in correlation_matrix[ticker].items():
            if value > threshold: #number arbitrary, revise if necessary
                try:
                    correlated_pairs[ticker].extend([other_ticker])
                except KeyError:
                    correlated_pairs[ticker] = [other_ticker]

def finding_cointegrated_pairs(correlated_pairs):
    for ticker in correlated_pairs:
        for other_ticker in correlated_pairs[ticker]:
            results = cointergration_test(ticker, other_ticker)
            if results[0] < results[2][2]:
                try:
                    cointegrated_pairs[ticker].extend([other_ticker])
                except KeyError:
                    cointegrated_pairs[ticker] = [other_ticker]

def plotting_stocks(pair):
    plt.plot(data["Date"], data[pair[0]], label = pair[0])
    plt.plot(data["Date"], data[pair[1]], label = pair[1])
    plt.legend(loc='upper left', frameon=False)
    plt.show()

finding_correlated_pairs(correlation_matrix)
finding_cointegrated_pairs(correlated_pairs)
print(correlated_pairs)
print(cointegrated_pairs)


#plotting_stocks(["ACC", "ABCB"])
