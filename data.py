import pandas as pd

# The 11 ETFs used in the exploratory analysis come first; the rest are added in groups of four
# so that each larger universe contains the smaller ones (nested), with a mix of asset classes at every step.
UNIVERSE_ORDER = [
    'DBC', 'GLD', 'HYG', 'QQQ', 'SHY', 'TLT', 'XLB', 'XLE', 'XLI', 'XLU', 'XLY',  # N = 11
    'SPY', 'EFA', 'IEF', 'VNQ',                                                   # N = 15
    'XLF', 'XLK', 'EEM', 'LQD',                                                   # N = 19
    'XLV', 'XLP', 'VGK', 'TIP',                                                   # N = 23
    'IWM', 'EWJ', 'SLV', 'USO',                                                   # N = 27
]


def load_prices(path='etf_prices.csv'):
    return pd.read_csv(path, index_col=0, parse_dates=True)


def monthly_returns(prices):
    # Month-end adjusted closes -> simple monthly returns. The last month is dropped if the data stops before month end.
    month_end = prices.resample('ME').last()
    if prices.index[-1] < month_end.index[-1] - pd.offsets.BDay(1):
        month_end = month_end.iloc[:-1]
    return month_end.pct_change().iloc[1:]


def universe(n):
    return UNIVERSE_ORDER[:n]
