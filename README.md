# Pairs Trading Algorithm
This code is my implementation of pairs trading, or taking advantage of cointegrated pairs that have deviated away from the historical trends in the market by shorting the higher asset and longing the lower asset in order to hope that the pair reverts back to the mean.
After simulating 5 years worth of data, the model grew the initial $10,000 to $23,575.58, an annualized rate of 27%.

![](/Screen%20Shot%202021-01-11%20at%207.50.30%20PM.png)

## Methodology
The three important things needed for builing a model is:

Ensuring the pairs the model chooses are cointegrated
Ensuring that the cointegrated pairs will revert back to the mean
Ensuring that the mean reversion will take place in the near future
### Cointegration
In order to ensure cointegration, I used the augmented Dickey–Fuller test for time series. You could also use the Engle-Granger test and I included it in the model if you prefer that method.

### Mean Reversion
I used the Hurst exponent to decide whether the cointegrated pairs would revert back to the mean. A Hurst exponent of a time-series that is greater or equal to .5 will mean that the time-series, or trend, is peristant and therefore not tradeable.

### Time
Using the Ornstein-Uhlenbeck process for time-series, you can find the estimated time of the mean reversion. I set the default as 30 trading days, or about 6 weeks, but if you are more patient you can do 60 or even 120 days.

### Setting up
You will need to have Pandas, Numpy, Statsmodels, and yFinance Python libraries installed. Just simply put
```
pip install ______
```
for each library in your terminal.

Once everything is installed, run scraper.py to get the latest information off the Yahoo Finance API. Information will be stored locally.

## Simulation
To test the model with historical data, just run simulation.py. It will run 5 years worth of historical data and print out the trades it makes and when it sells. For example:
```
Shorted ARCC at 16.34 Bought CSII at 43.46
Stopped shorting ARCC at 16.79 Sold CSII at 46.11
$24728.13 started with $10000. 1011 days passed
Long Mean Reverted 44.8
```
The last line will either have Mean Reverted or Stop Loss. The former means that your assumptions were true and the latter means that the pair has deviated away from the norm such that your assumptions are wrong.

You might also see the line printed as well.
```
Pair put back into the trading pool
```
This is because the simulation takes out pairs that lost money for 100 days, then puts them back into the dictionary of cointegrated pairs.

## Model
Run the model and it will output the best tradable pair given the last 200 days worth of data. It should look something like
```
TEF Current Price:  4.39
TEF Stop Loss if stock goes above 4.82
TEF Stop shorting when stock drops to 3.35
HEP Current Price:  14.38
HEP Stop Loss if stock goes below 13.13
HEP Sell when stock reaches 16.99
```
Note: every different day you want to run the model, you have to run scraper.py as well to ensure accurate results.
