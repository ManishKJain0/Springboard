import pandas as pd
import quandl
from time import sleep

# Place API key provided by Quandl signup.
quandl.ApiConfig.api_key = ""

strticker_list = "M:/Code/Springboard/Capstone_Project_1/SPX_Constituents_2019-01-28.csv"
strreport_path = "E:/"

# Load up the list of constituent tickers and convert it to a list.
dfrtickers = pd.read_csv(strticker_list)
lsttickers = dfrtickers["Symbol"].to_list()

dfrdata = None
# Could not use the direct Quandl call, since sending all 500 tickers casuses an error, most likely the url gets too long.
# So loop through tickers and append to existing dataframe.
for strticker in lsttickers:
    if dfrdata is None:
        dfrdata = quandl.get_table('WIKI/PRICES', qopts = { 'columns': ['ticker', 'date', 'close'] }, ticker = strticker, date = { 'gte': '1990-01-01', 'lte': '2018-12-31' })
    else:
        dfrdata = dfrdata.append(quandl.get_table('WIKI/PRICES', qopts = { 'columns': ['ticker', 'date', 'close'] }, ticker = strticker, date = { 'gte': '1990-01-01', 'lte': '2018-12-31' }))
    print(strticker)
    sleep(2)

# Pivot dataframe so that each column is a constituent.
dfrdata = dfrdata.pivot(index="date", columns="ticker", values="close")

dfrdata.to_csv(strreport_path + "SPX_Prices_1990-2018.csv")