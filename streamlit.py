from matplotlib import pyplot as plt
import pandas as pd
import random
import numpy as np
import yfinance as yf
import streamlit as st

st.title("Comparison between CAPM and Random Stock Portfolio")
st.write("The Capital Asset Pricing Model (CAPM) is one of the fundamental theories in financial investment evaluation, providing a rigorous methodology to estimate the expected return of a financial asset based on its risk. However, the practical application of the CAPM has often raised questions and debates regarding its ability to accurately predict the actual returns on investments in a real-world context.")
st.write("Through an empirical approach, we intend to examine whether the CAPM can effectively identify financial assets that provide higher returns compared to a randomly constructed portfolio.")
st.write("The Capital Asset Pricing Model (CAPM) formula provides a methodology for determining the expected return of a financial asset based on its risk. The CAPM formula is expressed as follows:")
st.latex("E(Ri)=Rf+βi(E(Rm)−Rf)")
st.write("Where:")
st.write("•	**E(Ri)** is the expected return of financial asset i,")
st.write("•	**Rf** is the risk-free rate of return (such as the return on a government bond),")
st.write("•	**βi** is the beta coefficient of financial asset i, measuring its sensitivity to market movements,")
st.write("•	**E(Rm)** is the expected return of the market, and")
st.write("•	**(E(Rm)−Rf)** represents the market risk premium, i.e., the additional return investors require for bearing market risk.")
st.write("In summary, the CAPM formula relates the expected return of a financial asset to the expected return of the market and the market risk premium, adjusting this relationship based on the asset's sensitivity to market movements, represented by the beta coefficient. This model is widely used in finance to evaluate the expected return of an investment and determine if that return is adequate given the risk assumed.")

start='2022-01-01'
end='2022-12-31'
tickers = list(pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'])

n = int(st.number_input("Enter the number of random stocks you want in the portfolio: ", value=8, placeholder="Type a number..."))

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


portfolio_tickers = generate_tickers(n, tickers)


portfolio_prices = pd.DataFrame()
for ticker in portfolio_tickers:
   price = all_stocks[ticker]
   portfolio_prices[ticker] = price

st.write("**Opening prices of stocks**")
st.write(portfolio_prices)


portfolio_yield = portfolio_prices.pct_change(fill_method="ffill").dropna()

st.write("**Yield of stocks**")
st.write("Using the previously created dataframe, we computed the yield of both the portfolio and the S&P 500.")
st.write(portfolio_yield)


sp500_yield = sp500.pct_change(fill_method="ffill").dropna()

st.write("**S&P500 Yield**")
st.write(sp500_yield)

portfolio_yield['CSSPX.MI']=sp500_yield
cov_matrix = portfolio_yield.cov()
del portfolio_yield['CSSPX.MI']

sp500_variance = np.var(sp500_yield)

betas = []
for stock in portfolio_tickers:
  stock_beta = cov_matrix.loc[stock, "CSSPX.MI"]/sp500_variance
  betas.append(round(stock_beta, 3))

portflio_df = pd.DataFrame({"Ticker": portfolio_tickers, "Beta": betas, "Weight": 1/n})

st.write("**Beta stocks**")
st.write("The beta for each stock was calculated by dividing the covariance of the stock with respect to the S&P 500 by the variance of theS&P 500. The covariance matrix was generated using an existing Python function.")
code='''betas = [] 
  for stock in portfolio_tickers: 
    stock_beta = cov_matrix.loc[stock, "CSSPX.MI"]/sp500_variance 
    betas.append(round(stock_beta, 3))'''
st.code(code, language='python')
st.write(portflio_df)

beta_sum = 0
n = len(portfolio_tickers)
for index, row in portflio_df.iterrows():
  beta_sum += row['Beta']*row['Weight']

portfolio_beta = round(beta_sum, 3)

st.write("**Overall beta of the portfolio**")
st.write("By averaging the betas, we obtained the overall beta of the portfolio, which was necessary for applying the CAPM formula.")
st.write(portfolio_beta)

mean_yield_perc=0
for i in range(n):
  mean_yield_perc+=((portfolio_prices.iloc[len(portfolio_prices.index)-1, i]*100)/portfolio_prices.iloc[0, i])-100
mean_yield_perc/=n

st.write("**Portfolio Yield**")
st.write(round(mean_yield_perc, 2),"%")

sp500_yield_perc=((sp500.iloc[len(portfolio_prices.index)-1]*100)/sp500.iloc[0])-100

st.write("**S&P500 Yield**")
st.write(round(sp500_yield_perc, 2), "%")

ER=rfr.iloc[0]+portfolio_beta*(sp500_yield_perc-rfr.iloc[0])

st.write("**CAPM formula result**")
st.write("Regarding the risk-free rate, we utilized the rate evaluated on the day of stock purchase.")
st.write("Based on all gathered data, we calculated the ExpectedReturn and created a histogram comparing the yearly yields of the portfolio, Expected Return, and the S&P 500 from 2016 to 2022.")
st.write(round(ER,2),"%")


plt.style.use("ggplot")
indexs=np.arange(7)
width= 0.2

x=[2016, 2017, 2018, 2019, 2020, 2021, 2022]
y1=[21.02, 34.96, 3.8, 52.81, 18.88, 3.06, -13.44]
y2=[5.35, 2.53, -0.88, 22.37, 5.94, 29.7, -11.2]
y3=[13.33, 6.12, 1.69, 35.05, 7.04, 39.37, -14.29]

st.write("**Histogram of returns**")
st.write("Based on all gathered data, we calculated the ExpectedReturn and created a histogram comparing the yearly yields of the portfolio, Expected Return, and the S&P 500 from 2016 to 2022.")
plt.bar(indexs, y1, color="red", width=width, label="Portfolio Yield")
plt.bar(indexs+width, y2, color="#212121", width=width, label="Expected return")
plt.bar(indexs-width, y3, color="blue", width=width, label="S&P500")
plt.legend()
plt.xticks(indexs, x)
st.pyplot(plt.gcf())

st.write("**Conclusions**")
st.write("From the graph results, some preliminary conclusions can be drawn, but it's important to note that these deductions are based on a limited number of tests. Therefore, to obtain more robust confirmations, further tests would be necessary using different types of portfolios and varying risk levels.")
st.write("Lastly, the analysis revealed that the returns calculated using the CAPM formula and those of the portfolio are not correlated, confirming the initial suspicions raised.")


