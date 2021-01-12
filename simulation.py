import numpy as np
import pandas as pd
import statsmodels
from scraper import yFinanceScraper
from model import hurst_analysis, OLS, saved_tradable_pairs
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller as adf

num_data = pd.read_csv("historical-data.csv")
saved_pairs = pairs
#data cleaning as the cointegration test can't have any NaN values
data = pd.read_csv("normalized-historical-data.csv")
data.iloc[0] = data.iloc[1]
data = data.fillna(method='ffill')
data = data.dropna(1)


class Simulation(object):
    elim_pairs = pairs
    def __init__(self, days, money, reversion_time=45):
        self.day = 200
        self.days = int(days)
        self.tradable_pairs = saved_tradable_pairs
        self.money = money
        self.ori_amount = str(money)
        self.eliminated_pairs = {}
        self.holding_pair = False
        while days > 200:

            if self.holding_pair == True:
                if num_data[best_pair[0]].iloc[self.day] > short_info[0]:
                    self.money += self.sell(best_pair, trading_info[0], trading_info[1], trading_info[2], trading_info[3])
                    print("$" + str(round(self.money,2))  + " started with $" + self.ori_amount + ". " + str(self.day-200) + " days passed")
                    print("Short Stop Loss", round(short_info[1],2))
                    if best_pair[0] in self.tradable_pairs and best_pair[1] in self.tradable_pairs[best_pair[0]]:
                        self.tradable_pairs[best_pair[0]].remove(best_pair[1])
                    else:
                        self.tradable_pairs[best_pair[1]].remove(best_pair[0])
                    self.eliminated_pairs[best_pair[0]] = [best_pair[1], 100]
                    self.holding_pair = False
                    reversion_time = 30

                elif num_data[best_pair[0]].iloc[self.day] < short_info[1]:
                    self.money += self.sell(best_pair, trading_info[0], trading_info[1], trading_info[2], trading_info[3])
                    print("$" + str(round(self.money,2))  + " started with $" + self.ori_amount + ". " + str(self.day-200) + " days passed")
                    print("Short Mean Reverted", round(short_info[1],2))
                    if best_pair[0] in self.tradable_pairs and best_pair[1] in self.tradable_pairs[best_pair[0]]:
                        self.tradable_pairs[best_pair[0]].remove(best_pair[1])
                    else:
                        self.tradable_pairs[best_pair[1]].remove(best_pair[0])
                    self.eliminated_pairs[best_pair[0]] = [best_pair[1], 100]
                    self.holding_pair = False
                    reversion_time = 30

                elif num_data[best_pair[1]].iloc[self.day] < long_info[0]:
                    self.money += self.sell(best_pair, trading_info[0], trading_info[1], trading_info[2], trading_info[3])
                    print("$" + str(round(self.money,2))  + " started with $" + self.ori_amount + ". " + str(self.day-200) + " days passed")
                    print("Long Stop Loss", round(long_info[0],2))
                    if best_pair[0] in self.tradable_pairs and best_pair[1] in self.tradable_pairs[best_pair[0]]:
                        self.tradable_pairs[best_pair[0]].remove(best_pair[1])
                    else:
                        self.tradable_pairs[best_pair[1]].remove(best_pair[0])
                    self.eliminated_pairs[best_pair[0]] = [best_pair[1], 100]
                    self.holding_pair = False
                    reversion_time = 30

                elif num_data[best_pair[1]].iloc[self.day] > long_info[1]:
                    self.money += self.sell(best_pair, trading_info[0], trading_info[1], trading_info[2], trading_info[3])
                    print("$" + str(round(self.money,2))  + " started with $" + self.ori_amount + ". " + str(self.day-200) + " days passed")
                    print("Long Mean Reverted",  round(long_info[1],2))
                    if best_pair[0] in self.tradable_pairs and best_pair[1] in self.tradable_pairs[best_pair[0]]:
                        self.tradable_pairs[best_pair[0]].remove(best_pair[1])
                    else:
                        self.tradable_pairs[best_pair[1]].remove(best_pair[0])
                    self.eliminated_pairs[best_pair[0]] = [best_pair[1], 100]
                    self.holding_pair = False
                    reversion_time = 30

                elif reversion_time == 0:
                    self.money += self.sell(best_pair, trading_info[0], trading_info[1], trading_info[2], trading_info[3])
                    print("$" + str(round(self.money,2))  + " started with $" + self.ori_amount + ". " + str(self.day-200) + " days passed")
                    print("Holding position greater than reversion time")
                    if best_pair[0] in self.tradable_pairs and best_pair[1] in self.tradable_pairs[best_pair[0]]:
                        self.tradable_pairs[best_pair[0]].remove(best_pair[1])
                    else:
                        self.tradable_pairs[best_pair[1]].remove(best_pair[0])
                    self.eliminated_pairs[best_pair[0]] = [best_pair[1], 100]
                    self.holding_pair = False
                    reversion_time = 30
            else:
                best_pair = self.find_best_pair(self.tradable_pairs)
                if best_pair == None or best_pair == []:
                    print("No Pairs on " + str(self.day))
                else:
                    short_info = self.entry_exit_points(best_pair)[0]
                    long_info = self.entry_exit_points(best_pair)[1]
                    trading_info = self.buy(best_pair, self.money)
                    self.holding_pair = True

            self.day += 1
            reversion_time -= 1
            days -= 1
            self.timer(self.eliminated_pairs)
        print(self.return_money())
    def finding_tradable_pairs(self, coint_pairs, dist=1.5):
        tradable_pairs = {}
        for ticker in coint_pairs:
            for other_ticker in coint_pairs[ticker]:
                pair = [ticker, other_ticker]
                bolli_bands = self.bollinger_bands(pair)
                ticker_last = data[ticker].iloc[self.day]
                other_ticker_last = data[other_ticker].iloc[self.day]
                upper_bolli_last = bolli_bands[0].iloc[-1]
                middle_bolli_last = bolli_bands[1].iloc[-1]
                lower_bolli_last = bolli_bands[2].iloc[-1]

                if (abs(ticker_last - middle_bolli_last) < dist and other_ticker_last < middle_bolli_last and ticker_last > middle_bolli_last
                    or abs(other_ticker_last - middle_bolli_last) < dist and ticker_last < middle_bolli_last and other_ticker_last > middle_bolli_last
                    or abs(ticker_last - middle_bolli_last) < dist and other_ticker_last > middle_bolli_last and ticker_last < middle_bolli_last
                    or abs(other_ticker_last - middle_bolli_last) < dist and ticker_last > middle_bolli_last and other_ticker_last < middle_bolli_last):

                    if ticker in tradable_pairs:
                        tradable_pairs[ticker].extend([other_ticker])
                    else:
                        tradable_pairs[ticker] = [other_ticker]

        return tradable_pairs



    def bollinger_bands(self, pair):

        combined_z_scores = (data[pair[0]].iloc[self.day-200:self.day] + data[pair[1]].iloc[self.day-200:self.day]) / 2
        upper_bolli_band = combined_z_scores + combined_z_scores.std() * 2
        lower_bolli_band = combined_z_scores - combined_z_scores.std() * 2
        return [upper_bolli_band, combined_z_scores, lower_bolli_band]

    def find_best_pair(self, pairs):
        best_pair = []
        minimum_ADF = 0
        for ticker in pairs:
            for other_ticker in pairs[ticker]:
                pair = [ticker, other_ticker]
                pair = (lambda pair: [ticker, other_ticker] if data[ticker].iloc[self.day] > data[other_ticker].iloc[self.day] else [other_ticker, ticker]) (pair)
                if self.ADF_test(ticker, other_ticker)[4]["1%"] < minimum_ADF and (self.entry_exit_points(pair)[0][0] > num_data[pair[0]].iloc[self.day] > self.entry_exit_points(pair)[0][1]
                                                                          and self.entry_exit_points(pair)[1][0] < num_data[pair[1]].iloc[self.day] < self.entry_exit_points(pair)[1][1]):

                    minimum_ADF = self.ADF_test(ticker, other_ticker)[4]["1%"]
                    best_pair = pair

        return best_pair

    def entry_exit_points(self, pair):
        bolli_bands = self.bollinger_bands(pair)
        middle_bolli_last = bolli_bands[1].iloc[-1] #also known as the moving average
        ticker0_rec = data[pair[0]].iloc[self.day]
        ticker1_rec = data[pair[1]].iloc[self.day]
        short_stock, long_stock = pair[0], pair[1]
        if abs(middle_bolli_last - ticker0_rec) > abs(middle_bolli_last - ticker1_rec):
            short_stock_exit = [round((num_data[short_stock].iloc[self.day] + num_data[short_stock].iloc[self.day-200:self.day].std() * 1), 2),
                                round((middle_bolli_last * num_data[short_stock].iloc[self.day-200:self.day].std()) + num_data[short_stock].iloc[self.day-200:self.day].mean(),2)]
            long_stock_exit = [round((num_data[long_stock].iloc[self.day] - num_data[long_stock].iloc[self.day-200:self.day].std() * 1), 2),
                                round((middle_bolli_last * num_data[long_stock].iloc[self.day-200:self.day].std() * 2) + num_data[long_stock].iloc[self.day-200:self.day].mean(), 2)]
        else:
            short_stock_exit = [round((num_data[short_stock].iloc[self.day] + num_data[short_stock].iloc[self.day-200:self.day].std() * 1), 2),
                                round((middle_bolli_last * num_data[short_stock].iloc[self.day-200:self.day].std() * 2) + num_data[short_stock].iloc[self.day-200:self.day].mean(),2)]
            long_stock_exit = [round((num_data[long_stock].iloc[self.day] - num_data[long_stock].iloc[self.day-200:self.day].std() * 1), 2),
                                round((middle_bolli_last * num_data[long_stock].iloc[self.day-200:self.day].std()) + num_data[long_stock].iloc[self.day-200:self.day].mean(), 2)]
        return [short_stock_exit, long_stock_exit]

    def buy(self, pair, money):
        short_last = num_data[pair[0]].iloc[self.day]
        long_last = num_data[pair[1]].iloc[self.day]
        short_amount = (self.money / 2) / short_last
        long_amount = (self.money / 2) / long_last
        print("Shorted " + pair[0] + " at " + str(round(short_last, 2)) + " Bought " + pair[1] + " at " + str(round(long_last, 2)))
        return [short_last, short_amount, long_last, long_amount]

    def sell(self, pair, short_orginal, short_amount, long_original, long_amount):
        short_last = num_data[pair[0]].iloc[self.day]
        long_last = num_data[pair[1]].iloc[self.day]
        print("Stopped shorting " + pair[0] + " at " + str(round(short_last, 2)) + " Sold " + pair[1] + " at " + str(round(long_last, 2)))
        return (short_orginal - short_last) * short_amount + (long_last - long_original) * long_amount

    def OLS(self, ticker1, ticker2):
        spread = sm.OLS(data[ticker1].iloc[self.day-200:self.day],data[ticker2].iloc[self.day-200:self.day])
        spread = spread.fit()
        return data[ticker1] + (data[ticker2] * -spread.params[0])

    def ADF(self,spread):
        return statsmodels.tsa.stattools.adfuller(spread)

    def ADF_test(self,ticker1, ticker2):
        return self.ADF(self.OLS(ticker1, ticker2))

    def return_money(self):
        return str(self.money)


    def timer(self, pairs):
        for ticker in pairs.copy().keys():
            if pairs[ticker][1] != 0:
                pairs[ticker][1] -= 1
            else:
                if ticker in self.tradable_pairs:
                    self.tradable_pairs[ticker].append(pairs[ticker][0])
                    pairs.pop(ticker)
                    print("Pair put back into the trading pair pool")

                else:
                    self.tradable_pairs[ticker] = [pairs[ticker][0]]
                    pairs.pop(ticker)
                    print("Pair put back into the trading pair pool")

Simulation(1215, 10000)
