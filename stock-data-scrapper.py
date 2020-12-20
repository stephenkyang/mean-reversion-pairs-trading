import pandas as pd
import yfinance as yf



class yFinanceScrapper(object):
    ticker_data = {}
    def __init__(self,names):
        self.names = names
        for ticker in self.names[0:10]:
            ticker = yf.Ticker(ticker)
            data = ticker.history(period="10y").loc[: , ["Open", "Close"]]
            yFinanceScrapper.ticker_data[ticker] = data


data = pd.read_csv("/Users/stephen/Desktop/Pairs Trading Project/data.csv")
data = data[data["Volume"] > 10000][data["IPO Year"] < 2010][data["Symbol"] != "AMHC"]["Symbol"]

#for real time use
#scraper = yFinanceScrapper(data)
print(yFinanceScrapper.ticker_data)

#for storing testing data

ticker_names = ""
for ticker in data:
    ticker_names += ticker + " "
ticker_download = yf.download(ticker_names, start="2010-01-01", end="2020-01-01", group_by="ticker")
ticker_download.to_csv("historical-ticker-data.csv", index = False)
