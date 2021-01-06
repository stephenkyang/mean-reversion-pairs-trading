import numpy as np
import pandas as pd
import statsmodels
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller as adf
import matplotlib.pyplot as plt
import statsmodels.tsa.vector_ar.vecm
from numpy import polyfit, sqrt, std, subtract, log
from scraper import yFinanceScraper
from dict_of_pairs import pairs

num_data = pd.read_csv("historical-data.csv")
saved_pairs = pairs
#data cleaning as the cointegration test can't have any NaN values
data = pd.read_csv("normalized-historical-data.csv")
data.iloc[0] = data.iloc[1]
data = data.fillna(method='ffill')
data = data.dropna(1)

data = data[data.columns[:]]
print(data.isnull().values.any())

# 1. Do the necessary regression models to find cointegrating pairs, whether that be ADF, EGranger, or Johansen (done)
# 2. Find pairs with wide spreads, through the calculation of the Hurst exponent and calculating the half-life of the mean reversion (done)
# 3. Output certain pairs that are cointergrated/correlated (done)
# 4. Add the ability to set entry and exit points (done)

#correlation and cointegrating section (Currently using ADF)
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


#have the bollinger bands of the ratio of two pairs, select a pair if one ticker is above the moving day avg and close to the
#top band and the other is below the moving day avg and close to the bottom band

def bollinger_bands(pair):
    combined_z_scores = data[pair[0]] + data[pair[1]]
    upper_bolli_band = combined_z_scores + combined_z_scores.std() * 2
    lower_bolli_band = combined_z_scores - combined_z_scores.std() * 2
    return [upper_bolli_band, combined_z_scores, lower_bolli_band]


correlation_matrix = correlation(data)

correlated_pairs = {}
cointegrated_pairs = {}
tradable_pairs = {}

#using correlation to eliminate clearly non-cointegrated pairs for efficency
def finding_correlated_pairs(correlation_matrix, threshold =.8): #threshold arbitrary, revise if necessary
    for ticker in correlation_matrix:
        for other_ticker, value in correlation_matrix[ticker].items():
            if value > threshold and value != 1.00 and (other_ticker not in correlated_pairs
                                                                    or ticker not in correlated_pairs[other_ticker]):
                try:
                    correlated_pairs[ticker].extend([other_ticker])
                except KeyError:
                    correlated_pairs[ticker] = [other_ticker]



def finding_cointegrated_pairs(corr_pairs, reversion_time=30):
    for ticker in corr_pairs:
        for other_ticker in corr_pairs[ticker]:
            results = ADF_test(ticker, other_ticker)
            if results[0] < results[4]["1%"] and (hurst_analysis(OLS(ticker, other_ticker)) < .5
                                                and half_life(OLS(ticker, other_ticker)) < reversion_time):
                try:
                    cointegrated_pairs[ticker].extend([other_ticker])
                except KeyError:
                    cointegrated_pairs[ticker] = [other_ticker]


def finding_tradable_pairs(coint_pairs, dist=2.5):
    for ticker in coint_pairs:
        for other_ticker in coint_pairs[ticker]:
            pair = [ticker, other_ticker]
            bolli_bands = bollinger_bands(pair)
            ticker_last = data[ticker].iloc[-1]
            other_ticker_last = data[other_ticker].iloc[-1]
            upper_bolli_last = bolli_bands[0].iloc[-1]
            middle_bolli_last = bolli_bands[1].iloc[-1]
            lower_bolli_last = bolli_bands[2].iloc[-1]

            if (abs(ticker_last - upper_bolli_last) < dist and other_ticker_last < middle_bolli_last
                or abs(ticker_last - upper_bolli_last) < dist and other_ticker_last < middle_bolli_last
                or abs(ticker_last - lower_bolli_last) < dist and other_ticker_last > middle_bolli_last
                or abs(ticker_last - lower_bolli_last) < dist and other_ticker_last > middle_bolli_last):

                try:
                    tradable_pairs[ticker].extend([other_ticker])
                except KeyError:
                    tradable_pairs[ticker] = [other_ticker]


#checking mean reversion (using Hurst exponents)
def hurst_analysis(spread):
    lags = range(2, (lambda: 100 if int(yFinanceScraper.period) > 100 else int(yFinanceScraper.period) - 1)())
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



def plotting_stocks(pair): #with bollinger bands
    plt.plot(bollinger_bands([pair[0], pair[1]])[0], label = "Upper Bollinger Band", color= "black")
    plt.plot(bollinger_bands([pair[0], pair[1]])[1], label = "Combined Z-score Average", color = "black")
    plt.plot(bollinger_bands([pair[0], pair[1]])[2], label = "Lower Bollinger Band", color = "black")
    plt.plot(data[pair[0]], label = pair[0])
    plt.plot(data[pair[1]], label = pair[1])
    plt.legend(loc='upper left', frameon=False)
    plt.show()


def entry_exit_points(pair):
    bolli_bands = bollinger_bands(pair)
    middle_bolli_last = bolli_bands[1].iloc[-1] #also known as the moving average
    ticker0_rec = data[pair[0]].iloc[-1]
    ticker1_rec = data[pair[1]].iloc[-1]
    short_stock, long_stock = (lambda pair: (pair[0], pair[1]) if ticker0_rec > ticker1_rec else (pair[1], pair[0])) (pair)
    print(short_stock + " Current Price: ",  round(num_data[short_stock].iloc[-1], 2))
    print(short_stock + " Stop Loss if stock goes above",  round((num_data[short_stock].iloc[-1] + num_data[short_stock].std() * 1.5), 2))
    print(short_stock + " Stop shorting when stock drops to",  round((middle_bolli_last * num_data[short_stock].std()) + num_data[short_stock].mean(),2))
    print(long_stock + " Current Price: ", round(num_data[long_stock].iloc[-1], 2))
    print(long_stock + " Stop Loss if stock goes below",  round((num_data[long_stock].iloc[-1] - num_data[short_stock].std() * 1.5), 2))
    print(long_stock + " Sell when stock reaches", round((middle_bolli_last * num_data[long_stock].std()) + num_data[long_stock].mean(), 2))
    plotting_stocks(pair)


#if you have one stock already
def finding_existing_pair(ticker, data, reversion_time = 30, corr_threshold = .9, dist = 2):
    potential_pairs = []
    for other_ticker in data:
        if (other_ticker == "Date" or other_ticker == ticker):
            pass
        else:
            if data[ticker].corr(data[other_ticker]) < corr_threshold:
                pass
            else:
                results = ADF_test(ticker, other_ticker)
                if results[0] < results[4]["1%"] and (hurst_analysis(OLS(ticker, other_ticker)) < .5
                                                    and half_life(OLS(ticker, other_ticker)) < reversion_time):
                    pair = [ticker, other_ticker]
                    bolli_bands = bollinger_bands(pair)
                    ticker_last = data[ticker].iloc[-1]
                    other_ticker_last = data[other_ticker].iloc[-1]
                    upper_bolli_last = bolli_bands[0].iloc[-1]
                    middle_bolli_last = bolli_bands[1].iloc[-1]
                    lower_bolli_last = bolli_bands[2].iloc[-1]

                    if (abs(ticker_last - upper_bolli_last) < dist and other_ticker_last < middle_bolli_last
                        or abs(ticker_last - upper_bolli_last) < dist and other_ticker_last < middle_bolli_last
                        or abs(ticker_last - lower_bolli_last) < dist and other_ticker_last > middle_bolli_last
                        or abs(ticker_last - lower_bolli_last) < dist and other_ticker_last > middle_bolli_last):

                        potential_pairs.append(other_ticker)
    return potential_pairs

#tests

"""
print(half_life(OLS("A","ASTE")))
"""

finding_tradable_pairs(saved_pairs)
print(tradable_pairs)

"""
print(finding_existing_pair("MSFT", data))
"""

"""
print(ADF_test("MSFT", "ELTK"))
plt.plot(OLS("MSFT", "ELTK"))
plt.show()
"""

entry_exit_points(["MVO", "VSAT"])
