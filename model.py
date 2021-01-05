import numpy as np
import pandas as pd
import statsmodels
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller as adf
import matplotlib.pyplot as plt
import statsmodels.tsa.vector_ar.vecm
from numpy import polyfit, sqrt, std, subtract, log

#data cleaning as the conintegration test can't have any NaN values

data = pd.read_csv("historical-data.csv")
data = data.replace("", np.nan, regex=True)
data = data.fillna(method='ffill')
data = data.dropna(1)
data = data[data.columns[0:100]]


# 1. Do the necessary regression models to find cointegrating pairs, whether that be ADF, EGranger, or Johansen
# 2. Find pairs with wide spreads, through the calculation of the Hurst exponent
# 3. Output certain pairs that are cointergrated/correlated
# 4. (Optional) Build a simple GUI that helps visualize the cointegration/spreads
# 5. (Optional) Make it live?

#correlation and cointegrating section (Currently using EGranger)
def correlation(data):
    corr_mat = data.corr()
    return corr_mat

#EGranger test
def cointergration_test(ticker1, ticker2):
    return statsmodels.tsa.stattools.coint(data[ticker1],data[ticker2])

#ADF test
#run Odinary Least Squares regression to find hedge ratio and then create spread series
def OLS(ticker1, ticker2):
    spread = sm.OLS(data[ticker1],data[ticker2])
    spread = spread.fit()
    return data[ticker1] + (data[ticker2] * -spread.params[0])

#ADF uses the spread of the two stocks, also calculated through
def ADF(spread):
    return statsmodels.tsa.stattools.adfuller(spread)

def finding_ADF_pairs(ticker1, ticker2):
    return ADF(OLS(ticker1, ticker2))

correlation_matrix = correlation(data)

correlated_pairs = {}
cointegrated_pairs = {}

#using correlation to eliminate clearly non-cointegrated pairs for efficency
def finding_correlated_pairs(correlation_matrix, threshold =.9): #threshold arbitrary, revise if necessary
    for ticker in correlation_matrix:
        for other_ticker, value in correlation_matrix[ticker].items():
            if value > threshold and value != 1.00:
                try:
                    correlated_pairs[ticker].extend([other_ticker])
                except KeyError:
                    correlated_pairs[ticker] = [other_ticker]


def finding_cointegrated_pairs(corr_pairs):
    for ticker in corr_pairs:
        for other_ticker in corr_pairs[ticker]:
            results = finding_ADF_pairs(ticker, other_ticker)
            if results[0] < results[4]["1%"]:
                try:
                    cointegrated_pairs[ticker].extend([other_ticker])
                except KeyError:
                    cointegrated_pairs[ticker] = [other_ticker]
"""
finding_correlated_pairs(correlation_matrix)
finding_cointegrated_pairs(correlated_pairs)
print(cointegrated_pairs)
"""
#checking mean reversion (using Hurst exponents)
def hurst_analysis(spread):
    lags = range(2, 100)
    tau = [sqrt(std(subtract(spread[lag:], spread[:-lag]))) for lag in lags]
    print(tau)
    poly = polyfit(log(lags), log(tau), 1)
    return poly[0]*2

print(hurst_analysis(OLS("A", "ANSS")))

def plotting_stocks(pair):
    plt.plot(data["Date"], data[pair[0]], label = pair[0])
    plt.plot(data["Date"], data[pair[1]], label = pair[1])
    plt.legend(loc='upper left', frameon=False)
    plt.show()
