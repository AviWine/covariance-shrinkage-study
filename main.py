import pandas as pd

sp500 = pd.read_csv('sp500.csv', index_col=0)
print(sp500.loc['2020-05-01'])