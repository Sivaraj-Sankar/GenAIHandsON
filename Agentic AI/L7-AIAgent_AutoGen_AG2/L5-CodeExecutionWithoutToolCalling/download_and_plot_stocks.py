# filename: download_and_plot_stocks.py
from functions import get_stock_prices, plot_stock_prices
import datetime
import pandas as pd

# Define the stock symbols and end date
stock_symbols = ['NVDA', 'TSLA']
end_date = "2025-05-23"
start_date = "2025-01-01"

# Fetching the stock prices
stock_prices = get_stock_prices(stock_symbols, start_date, end_date)

# Plotting the stock prices
plot_stock_prices(stock_prices, 'stock_prices_YTD_plot.png')

print("Stock price plot has been created and saved as 'stock_prices_YTD_plot.png'.")