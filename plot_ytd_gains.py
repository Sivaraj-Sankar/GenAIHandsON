# filename: plot_ytd_gains.py
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

def fetch_stock_data(stock_symbol, start_date, end_date):
    # Fetch historical data from Yahoo Finance
    try:
        data = yf.download(stock_symbol, start=start_date, end=end_date)
        if data.empty:
            raise ValueError(f"No data fetched for {stock_symbol}. The symbol may be incorrect or unavailable.")
        return data
    except Exception as e:
        print(f"Error fetching data for {stock_symbol}: {e}")
        return pd.DataFrame()  # Return an empty dataframe in case of any error

def calculate_ytd_gain(data):
    if not data.empty:
        # Calculate the gains relative to the first trading day close price using .iloc
        ytd_gain = (data['Close'] / data['Close'].iloc[0] - 1) * 100
        return ytd_gain
    else:
        return pd.Series()  # Return an empty series if data is empty

def plot_stock_gains(dates, gains_nvda, gains_tsla):
    if not gains_nvda.empty and not gains_tsla.empty:
        plt.figure(figsize=(10, 6))
        plt.plot(dates, gains_nvda, label='NVIDIA (NVDA)', marker='o')
        plt.plot(dates, gains_tsla, label='Tesla (TSLA)', marker='o')
        plt.title('YTD Stock Gains for NVIDIA and Tesla in 2025')
        plt.xlabel('Date')
        plt.ylabel('Percentage Gain')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('ytd_stock_gains.png')
        plt.show()

# Define the time period
start_date = '2025-01-01'
end_date = '2025-05-23'

# Fetch data
nvda_data = fetch_stock_data('NVDA', start_date, end_date)
tsla_data = fetch_stock_data('TSLA', start_date, end_date)

# Calculate YTD gains
nvda_gains = calculate_ytd_gain(nvda_data)
tsla_gains = calculate_ytd_gain(tsla_data)

# Plot the data
plot_stock_gains(nvda_data.index if not nvda_data.empty else [], nvda_gains, tsla_gains)