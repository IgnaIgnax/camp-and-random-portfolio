from matplotlib import pyplot as plt
import pandas as pd
import random
import numpy as np
import yfinance as yf

start='2022-01-03'
end='2022-12-29'
tickers = list(pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'])

#Download and clean prices dataframe
all_stocks = yf.download(tickers, start=start, end=end)['Open']
sp500=yf.download('CSSPX.MI', start=start, end=end)['Open']
all_stocks.dropna(axis='columns', how='any', inplace=True)

#Upload tickers list
rfr=yf.download("^IRX", start=start)['Open']
tickers = all_stocks.columns.tolist()

def generate_tickers(n, tickers):
  portfolio = []
  arr = random.sample(range(len(tickers)), n)

  for x in arr:
    portfolio.append(tickers[x])
  return portfolio

n = int(input("Enter the number of random stocks to include in the stock portfolio:"))
portfolio_tickers = generate_tickers(n, tickers)

print("Portfolio Tickers: ")
print(portfolio_tickers)

# Scarico dati delle stocks del portafoglio

portfolio_prices = pd.DataFrame()
for ticker in portfolio_tickers:
   price = all_stocks[ticker]
   portfolio_prices[ticker] = price


print("\n\nPortfoglio prices: ")
print(portfolio_prices)

portfolio_yield = portfolio_prices.pct_change(fill_method="ffill").dropna()

sp500_yield = sp500.pct_change(fill_method="ffill").dropna()

portfolio_yield['CSSPX.MI']=sp500_yield
cov_matrix = portfolio_yield.cov()
del portfolio_yield['CSSPX.MI']

sp500_variance = np.var(sp500_yield)

betas = []
for stock in portfolio_tickers:
  stock_beta = cov_matrix.loc[stock, "CSSPX.MI"]/sp500_variance
  betas.append(round(stock_beta, 3))

portflio_df = pd.DataFrame({"Ticker": portfolio_tickers, "Beta": betas, "Weight": 1/n})

print(portflio_df)

beta_sum = 0
n = len(portfolio_tickers)
for index, row in portflio_df.iterrows():
  beta_sum += row['Beta']*row['Weight']

portfolio_beta = round(beta_sum, 3)

print("\n\nPortfoglio beta: ")
print(portfolio_beta)

mean_yield_perc=0
for i in range(n):
  mean_yield_perc+=((portfolio_prices.iloc[len(portfolio_prices.index)-1, i]*100)/portfolio_prices.iloc[0, i])-100
mean_yield_perc/=n

print("\n\nPortfoglio yield: ")
print(round(mean_yield_perc, 2),"%")

sp500_yield_perc=((sp500.iloc[len(portfolio_prices.index)-1]*100)/sp500.iloc[0])-100

print("\n\nS&P500 yield: ")
print(round(sp500_yield_perc, 2), "%")

ER=rfr.loc[start]+portfolio_beta*(sp500_yield_perc-rfr.loc[start])
print("\n\nCAPM Formula: ")
print(round(ER,2),"%")

plt.style.use("ggplot")
indexs=np.arange(7)
width= 0.2

x=[2016, 2017, 2018, 2019, 2020, 2021, 2022]
y1=[21.02, 34.96, 3.8, 52.81, 18.88, 3.06, -13.44]
y2=[5.35, 2.53, -0.88, 22.37, 5.94, 29.7, -11.2]
y3=[13.33, 6.12, 1.69, 35.05, 7.04, 39.37, -14.29]



plt.bar(indexs, y1, color="red", width=width, label="Portfolio Yield")
plt.bar(indexs+width, y2, color="#212121", width=width, label="Expected return")
plt.bar(indexs-width, y3, color="blue", width=width, label="S&P500")
plt.legend()
plt.xticks(indexs, x)
plt.show()


