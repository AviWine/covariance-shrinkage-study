import yfinance as yf
import pandas as pd

#download sp500 for analysis purposes
sp500 = yf.download('^GSPC', start='2000-01-01', end ='2025-12-31')
sp500.to_csv('sp500.csv')

tickers = [
    # US equity
    "SPY", "QQQ", "IWM",
    # US sectors
    "XLK", "XLF", "XLE", "XLV", "XLY", "XLP", "XLI", "XLU", "XLB",
    # International equity
    "EFA", "EEM", "VGK", "EWJ",
    # Bonds
    "SHY", "IEF", "TLT", "LQD", "HYG", "TIP",
    # Real estate and commodities
    "VNQ", "GLD", "SLV", "DBC", "USO",
]

prices = yf.download(
    tickers,
    start="2008-01-01",
    end="2026-10-12",
    auto_adjust=True,
    progress=False,
)["Close"]

prices.to_csv("etf_prices.csv")