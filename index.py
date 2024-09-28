from matplotlib import pyplot as plt
import pandas as pd
import random
import numpy as np
import yfinance as yf

# Get the S&P 500 tickers
tickers = list(pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'])

# Function to generate a random portfolio of tickers
def generate_tickers(n, tickers):
    return random.sample(tickers, n)

# Get user input for the number of stocks in the portfolio
n = int(input("Enter the number of random stocks to include in the stock portfolio: "))
portfolio_tickers = generate_tickers(n, tickers)

print("Portfolio Tickers: ")
print(portfolio_tickers)

# Initialize empty DataFrame for portfolio prices
portfolio_prices = pd.DataFrame()

# Download data for the randomly selected tickers
for ticker in portfolio_tickers:
    try:
        # Download price data
        price_data = yf.download(ticker, start='2016-01-01', end='2023-12-31')['Open']
        # Add to the DataFrame if data is available
        portfolio_prices[ticker] = price_data
    except Exception as e:
        print(f"Could not download data for {ticker}: {e}")

# Drop tickers that do not have any data
portfolio_prices.dropna(axis='columns', how='all', inplace=True)

# Determine the available date range based on the downloaded data
if not portfolio_prices.empty:
    start_date = portfolio_prices.index.min()
    end_date = portfolio_prices.index.max()
else:
    print("No data available for the selected tickers. Please try again.")
    exit()

print(f"Data available from {start_date.date()} to {end_date.date()}")

# Download the S&P 500 index data for the same date range
sp500 = yf.download('^GSPC', start=start_date, end=end_date)['Open']
sp500.dropna(inplace=True)  # Clean S&P 500 data

# Download the risk-free rate data for the same date range
rfr = yf.download("^IRX", start=start_date, end=end_date)['Open']
rfr.dropna(inplace=True)  # Clean risk-free rate data

# Check if there are enough tickers with available data
if portfolio_prices.empty:
    print("No data available for the selected tickers. Please try again.")
else:
    # Calculate the percentage change (yields)
    portfolio_yield = portfolio_prices.pct_change(fill_method="ffill").dropna()
    sp500_yield = sp500.pct_change(fill_method="ffill").dropna()

    # Combine portfolio yields with S&P 500 yields
    portfolio_yield['SP500'] = sp500_yield

    # Calculate the covariance matrix
    cov_matrix = portfolio_yield.cov()
    del portfolio_yield['SP500']  # Remove S&P 500 yield from the portfolio yields

    # Calculate S&P 500 variance
    sp500_variance = np.var(sp500_yield)

    # Calculate beta for each stock in the portfolio
    betas = []
    for stock in portfolio_tickers:
        if stock in cov_matrix.index:  # Check if the stock has data
            stock_beta = cov_matrix.loc[stock, "SP500"] / sp500_variance
            betas.append(round(stock_beta, 3))
        else:
            betas.append(np.nan)  # Assign NaN if no data

    # Create a DataFrame for the portfolio
    portfolio_df = pd.DataFrame({"Ticker": portfolio_tickers, "Beta": betas, "Weight": 1/n})

    # Drop rows with NaN betas
    portfolio_df.dropna(subset=['Beta'], inplace=True)

    print(portfolio_df)

    # Calculate portfolio beta
    portfolio_beta = (portfolio_df['Beta'] * portfolio_df['Weight']).sum()

    print("\n\nPortfolio beta: ")
    print(round(portfolio_beta, 3))

    # Calculate mean yield percentage of the portfolio
    mean_yield_perc = portfolio_prices.iloc[-1] / portfolio_prices.iloc[0] * 100 - 100
    mean_yield_perc = mean_yield_perc.mean()

    print("\n\nPortfolio yield: ")
    print(round(mean_yield_perc, 2), "%")

    # Calculate S&P 500 yield percentage
    sp500_yield_perc = (sp500.iloc[-1] / sp500.iloc[0] * 100) - 100

    print("\n\nS&P500 yield: ")
    print(round(sp500_yield_perc, 2), "%")

    # Calculate expected return using CAPM
    ER = rfr.loc[start_date] + portfolio_beta * (sp500_yield_perc - rfr.loc[start_date])
    print("\n\nCAPM Formula: ")
    print(round(ER, 2), "%")

    # Prepare data for plotting
    years = portfolio_prices.index.year.unique()
    portfolio_yields = []

    # Calculate yearly yields for the portfolio
    for year in years:
        yearly_prices = portfolio_prices[portfolio_prices.index.year == year]
        if not yearly_prices.empty:
            yearly_yield = (yearly_prices.iloc[-1] / yearly_prices.iloc[0] * 100) - 100
            portfolio_yields.append(yearly_yield.mean())
        else:
            portfolio_yields.append(np.nan)

    # Calculate expected return over the years (dummy data for illustration)
    expected_returns = [ER] * len(years)  # Using the calculated ER for all years
    sp500_yields = []

    # Calculate yearly yields for S&P 500
    for year in years:
        yearly_sp500 = sp500[sp500.index.year == year]
        if not yearly_sp500.empty:
            yearly_sp500_yield = (yearly_sp500.iloc[-1] / yearly_sp500.iloc[0] * 100) - 100
            sp500_yields.append(yearly_sp500_yield)
        else:
            sp500_yields.append(np.nan)

    # Plotting the results
    plt.style.use("ggplot")
    indexs = np.arange(len(years))
    width = 0.2

    plt.bar(indexs, portfolio_yields, color="red", width=width, label="Portfolio Yield")
    plt.bar(indexs - width, sp500_yields, color="blue", width=width, label="S&P500")
    plt.legend()
    plt.xticks(indexs, years)
    plt.xlabel('Year')
    plt.ylabel('Yield (%)')
    plt.title('Comparison of Portfolio and S&P 500 Yields')
    plt.show()
