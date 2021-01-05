import numpy as np
import pandas as pd
import statsmodels
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller as adf
import matplotlib.pyplot as plt
import statsmodels.tsa.vector_ar.vecm
from numpy import polyfit, sqrt, std, subtract, log

#data cleaning as the cointegration test can't have any NaN values

data = pd.read_csv("historical-data.csv")
data.iloc[0] = data.iloc[1]
data = data.fillna(method='ffill')
data = data.dropna(1)

data = data[data.columns]


# 1. Do the necessary regression models to find cointegrating pairs, whether that be ADF, EGranger, or Johansen (done)
# 2. Find pairs with wide spreads, through the calculation of the Hurst exponent and calculating the half-life of
#    the mean reversion (done)
# 3. Output certain pairs that are cointergrated/correlated (done)
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

def ADF(spread):
    return statsmodels.tsa.stattools.adfuller(spread)

def ADF_test(ticker1, ticker2):
    return ADF(OLS(ticker1, ticker2))

correlation_matrix = correlation(data)

correlated_pairs = {}
cointegrated_pairs = {}

#using correlation to eliminate clearly non-cointegrated pairs for efficency
def finding_correlated_pairs(correlation_matrix, threshold =.9): #threshold arbitrary, revise if necessary
    for ticker in correlation_matrix:
        for other_ticker, value in correlation_matrix[ticker].items():
            if value > threshold and value != 1.00 and (other_ticker not in correlated_pairs
                                                                    or ticker not in correlated_pairs[other_ticker]):
                try:
                    correlated_pairs[ticker].extend([other_ticker])
                except KeyError:
                    correlated_pairs[ticker] = [other_ticker]



def finding_cointegrated_pairs(corr_pairs, reversion_time=15):
    for ticker in corr_pairs:
        for other_ticker in corr_pairs[ticker]:
            results = ADF_test(ticker, other_ticker)
            if results[0] < results[4]["1%"] and (hurst_analysis(OLS(ticker, other_ticker)) < .5
                                                and half_life(OLS(ticker, other_ticker)) < reversion_time):
                try:
                    cointegrated_pairs[ticker].extend([other_ticker])
                except KeyError:
                    cointegrated_pairs[ticker] = [other_ticker]



#checking mean reversion (using Hurst exponents)
def hurst_analysis(spread):
    lags = range(2, 100)
    tau = [sqrt(std(spread[lag:].subtract(spread[:-lag].values))) for lag in lags]
    poly = polyfit(log(lags), log(tau), 1)
    return poly[0]*2

#checking how long mean revision will take place
def half_life(spread):
    spread_lag = spread.shift(1)
    spread_lag.iloc[0] = spread_lag.iloc[1]
    spread_ret = spread - spread_lag.values
    spread_ret.iloc[0] = spread_ret.iloc[1]
    spread_lag2 = sm.add_constant(spread_lag)
    model = sm.OLS(spread_ret,spread_lag2)
    res = model.fit()
    return -np.log(2) / res.params[0]


"""
print(half_life(OLS("A","ASTE")))
"""

"""
finding_correlated_pairs(correlation_matrix)
finding_cointegrated_pairs(correlated_pairs)
print(cointegrated_pairs)
"""
"""
print(ADF_test("MSFT", "ELTK"))
plt.plot(OLS("MSFT", "ELTK"))
plt.show()
"""

def plotting_stocks(pair):
    plt.plot(data["Date"], data[pair[0]], label = pair[0])
    plt.plot(data["Date"], data[pair[1]], label = pair[1])
    plt.legend(loc='upper left', frameon=False)
    plt.show()

#if you have one stock already
def finding_existing_pair(ticker, data, reversion_time = 15):
    potential_pairs = []
    for other_ticker in data:
        if other_ticker == "Date" or other_ticker == ticker:
            pass
        else:
            results = ADF_test(ticker, other_ticker)
            if results[0] < results[4]["1%"] and (hurst_analysis(OLS(ticker, other_ticker)) < .5
                                                and half_life(OLS(ticker, other_ticker)) < reversion_time):
                    potential_pairs.append(other_ticker)
    return potential_pairs

plotting_stocks(["MSFT", "XIN"])
