# filename: download_and_plot_stocks_retry.py
from functions import get_stock_prices, plot_stock_prices
import time

# Define the stock symbols and the dates for YTD
stock_symbols = ['NVDA', 'TSLA']
end_date = '2025-05-23'
start_date = '2025-01-01'

# Attempt to fetch the stock prices
attempt = 0
max_attempts = 3
while attempt < max_attempts:
    try:
        stock_prices = get_stock_prices(stock_symbols, start_date, end_date)
        plot_stock_prices(stock_prices, 'stock_prices_YTD_plot.png')
        print("Stock price plot has been created and saved as 'stock_prices_YTD_plot.png'.")
        break
    except Exception as e:
        print(f"Attempt {attempt+1} failed: {e}")
        attempt += 1
        time.sleep(5)  # wait 5 seconds before retrying

if attempt == max_attempts:
    print("Failed to retrieve and plot stock prices after several attempts.")