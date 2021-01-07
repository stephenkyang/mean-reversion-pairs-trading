import numpy as np
import pandas as pd
import statsmodels
from scraper import yFinanceScraper
from model import hurst_analysis, OLS
from dict_of_pairs import pairs

num_data = pd.read_csv("historical-data.csv")
saved_pairs = pairs
#data cleaning as the cointegration test can't have any NaN values
data = pd.read_csv("normalized-historical-data.csv")
data.iloc[0] = data.iloc[1]
data = data.fillna(method='ffill')
data = data.dropna(1)


days = yFinanceScraper.period

class Simulation(object):

    def __init__(self, days, money, reversion_time=60):
        self.day = 200
        self.days = int(days)
        self.tradable_pairs = self.finding_tradable_pairs(saved_pairs, self.day)
        self.money = money
        self.ori_amount = str(money)
        self.holding_pair = False
        while days > 200:

            if self.holding_pair == True:
                if num_data[best_pair[0]].iloc[self.day] > short_info[0]:
                    self.money += self.sell(best_pair, trading_info[0], trading_info[1], trading_info[2], trading_info[3])
                    print("$" + str(round(self.money,2))  + " started with $" + self.ori_amount)
                    print("Short Stop Loss", short_info[0])
                    self.holding_pair = False
                elif num_data[best_pair[0]].iloc[self.day] < short_info[1]:
                    self.money += self.sell(best_pair, trading_info[0], trading_info[1], trading_info[2], trading_info[3])
                    print("$" + str(round(self.money,2))  + " started with $" + self.ori_amount)
                    print("Short Mean Reverted", short_info[1])
                    self.holding_pair = False
                elif num_data[best_pair[1]].iloc[self.day] < long_info[0]:
                    self.money += self.sell(best_pair, trading_info[0], trading_info[1], trading_info[2], trading_info[3])
                    print("$" + str(round(self.money,2))  + " started with $" + self.ori_amount)
                    print("Long Stop Loss", long_info[0])
                    self.holding_pair = False
                elif num_data[best_pair[1]].iloc[self.day] > long_info[1]:
                    self.money += self.sell(best_pair, trading_info[0], trading_info[1], trading_info[2], trading_info[3])
                    print("$" + str(round(self.money,2))  + " started with $" + self.ori_amount)
                    print("Long Mean Reverted",  long_info[1])
                    self.holding_pair = False
                elif reversion_time == 0:
                    self.money += self.sell(best_pair, trading_info[0], trading_info[1], trading_info[2], trading_info[3])
                    print("$" + str(round(self.money,2))  + " started with $" + self.ori_amount)
                    print("Holding position greater than reversion time")
                    self.holding_pair = False
            else:
                best_pair = self.find_best_pair(self.tradable_pairs)
                short_info = self.entry_exit_points(best_pair)[0]
                long_info = self.entry_exit_points(best_pair)[1]
                trading_info = self.buy(best_pair, self.money)
                self.holding_pair = True

            self.day+= 1
            reversion_time -= 1
            days -= 1
            print(self.return_money())

    def finding_tradable_pairs(self, coint_pairs, dist=5):
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

                if (abs(ticker_last - upper_bolli_last) < dist and other_ticker_last < middle_bolli_last and ticker_last > middle_bolli_last
                    or abs(other_ticker_last - upper_bolli_last) < dist and ticker_last < middle_bolli_last and other_ticker_last > middle_bolli_last
                    or abs(ticker_last - lower_bolli_last) < dist and other_ticker_last > middle_bolli_last and ticker_last < middle_bolli_last
                    or abs(other_ticker_last - lower_bolli_last) < dist and ticker_last > middle_bolli_last and other_ticker_last < middle_bolli_last):

                    if ticker in tradable_pairs:
                        tradable_pairs[ticker].extend([other_ticker])
                    else:
                        tradable_pairs[ticker] = [other_ticker]

        return tradable_pairs



    def bollinger_bands(self, pair):
        combined_z_scores = data[pair[0]].iloc[self.day-200:self.day] + data[pair[1]].iloc[self.day-200:self.day]
        upper_bolli_band = combined_z_scores + combined_z_scores.std() * 2
        lower_bolli_band = combined_z_scores - combined_z_scores.std() * 2
        return [upper_bolli_band, combined_z_scores, lower_bolli_band]

    def find_best_pair(self, pairs):
        best_pair = []
        minimum_hurst = .5
        for ticker in pairs:
            for other_ticker in pairs[ticker]:
                pair = [ticker, other_ticker]
                pair = (lambda pair: [ticker, other_ticker] if data[pair[0]].iloc[self.day] > data[pair[1]].iloc[self.day] else [other_ticker, ticker]) (pair)
                if hurst_analysis(OLS(pair[0], pair[1])) < minimum_hurst and (self.entry_exit_points(pair)[0][0] < data[pair[0]].iloc[self.day] > self.entry_exit_points(pair)[0][1]
                                                                          and self.entry_exit_points(pair)[1][0] < data[pair[1]].iloc[self.day] > self.entry_exit_points(pair)[1][1]):

                    minimum_hurst = hurst_analysis(OLS(pair[0], pair[1]))
                    best_pair = pair

        return best_pair

    def entry_exit_points(self, pair):
        bolli_bands = self.bollinger_bands(pair)
        middle_bolli_last = bolli_bands[1].iloc[-1] #also known as the moving average
        ticker0_rec = data[pair[0]].iloc[self.day]
        ticker1_rec = data[pair[1]].iloc[self.day]
        short_stock, long_stock = pair[0], pair[1]
        short_stock_exit = [round((num_data[short_stock].iloc[self.day] + num_data[short_stock].iloc[self.day-200:self.day].std() * 1.5), 2), round((middle_bolli_last * num_data[short_stock].iloc[self.day-200:self.day].std()) + num_data[short_stock].iloc[self.day-200:self.day].mean(),2)]
        long_stock_exit = [round((num_data[long_stock].iloc[self.day] - num_data[short_stock].iloc[self.day-200:self.day].std() * 1.5), 2), round((middle_bolli_last * num_data[long_stock].iloc[self.day-200:self.day].std()) + num_data[long_stock].iloc[self.day-200:self.day].mean(), 2)]

        return [short_stock_exit, long_stock_exit]

    def buy(self, pair, money):
        short_last = num_data[pair[0]].iloc[self.day]
        long_last = num_data[pair[1]].iloc[self.day]
        short_amount = (self.money / 2) / short_last
        long_amount = (self.money / 2) / long_last
        print("Shorted " + pair[0] + " at " + str(short_last) + " Bought " + pair[1] + " at " + str(long_last))
        return [short_last, short_amount, long_last, long_amount]

    def sell(self, pair, short_orginal, short_amount, long_original, long_amount):
        short_last = num_data[pair[0]].iloc[self.day]
        long_last = num_data[pair[1]].iloc[self.day]
        print("Stopped shorting " + pair[0] + " at " + str(short_last) + " Sold " + pair[1] + " at " + str(long_last))
        return (short_orginal - short_last) * short_amount + (long_original - long_last) * long_amount

    def return_money(self):
        return self.money



Simulation(400, 10000)
