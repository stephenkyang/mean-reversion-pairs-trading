import pandas as pd
import yfinance as yf

ticker_data = {}

class yFinanceScrapper(object):
    def __init__(self, ticker):
        self.ticker = yf.Ticker(ticker)
        self.data = self.ticker.history(period="10y").loc[: , ["Open", "Close"]]
        ticker_data[ticker] = self.data

data = pd.read_csv("/Users/stephen/Desktop/Pairs Trading Project/data.csv")
print(data["Symbol"])

for ticker in data["Symbol"]:
    yFinanceScrapper(ticker)
