import pandas as pd
import yfinance as yf

class yFinanceScraper(object):
    namelist = []
    first = True
    df = None
    def __init__(self,names):
        self.names = names
        self.historicallist= []
        for name in self.names[0:100]:
            self.namelist.append(name)
            ticker = yf.Ticker(name)
            data = ticker.history(period="1y").loc[: , ["Close"]]
            data = data.rename(columns={"Date": "Date", "Close": name})
            if self.first:
                self.df = data
                self.first = False
            else:
                self.df =  pd.concat([self.df, data], axis=1)


data = pd.read_csv("/Users/stephen/Desktop/Pairs Trading Project/ticker-names-on-NASDAQ-NYSE.csv")
data = data[data["Volume"] > 10000][data["IPO Year"] < 2010][data["Symbol"] != "AMHC"]["Symbol"]

#for storing testing data
scraper = yFinanceScraper(data)
scraper.df.to_csv("historical-data.csv")
#for real time use
