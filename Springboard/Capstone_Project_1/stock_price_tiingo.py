import requests
import pandas as pd
from time import sleep

"""
This module is used to download closing prices for a list of stock tickers. It requests it through a Yahoo URL.

The results are saved down in a csv.

"""
# Processes a list of tickers and gets underlying report type urls.
def stock_price_list(strticker, strstartdate, strenddate, strtoken):
    # Use requests-HTML to request page and traverse to correct HTML tags.
    lstreports = []
    dctheaders = {'Content-Type': 'application/json'}

    # Create dictionary of arguement strings that can be used to query stock prices from Tiingo.
    dctargs = {}
    dctargs["url"] = "https://api.tiingo.com/tiingo/daily/<ticker>/prices?"
    dctargs["startdate"] = "startdate="
    dctargs["enddate"]= "&endDate="
    dctargs["token"]= "&token="
    

    # Construct and send url.
    strrequest_url = dctargs["url"].replace("<ticker>", strticker).lower()
    strrequest_url += dctargs["startdate"] + strstartdate
    strrequest_url += dctargs["enddate"] + strenddate
    strrequest_url += dctargs["token"] + strtoken

    #response = requests.get("https://api.tiingo.com/tiingo/daily/mmm/prices?startDate=2019-01-02&token=e60403fe4c3106347171d0eb1962e75ceaedb357", headers=dctheaders)
    response = requests.get(strrequest_url, headers=dctheaders)
    # Check if request succeeded.
    if response.status_code == 200: # Standard response for successful HTTP requests.
        dfrdata = pd.read_json(response.text)
        dfrdata = dfrdata[["date", "adjClose"]]
        dfrdata = dfrdata.set_index("date").rename({"adjClose":strticker}, axis="columns")
        return dfrdata
    else:
        print("Failure occurred for company %s." % (strticker))

strticker_list = "M:/Code/Springboard/Capstone_Project_1/Capstone_Project_1/SPX_Constituents_2019-01-28.csv"
strreport_path = "E:/"
strstart_date = "2012-01-01" #Format YYYY-M-D
strend_date = "2019-01-01" #Format YYYY-M-D
strtoken = "e60403fe4c3106347171d0eb1962e75ceaedb357"

dctFilters = {"GICS Sector": "Financials", "GICS Sub Industry": None, "Symbol": None}
# Load up the list of constituent tickers and convert it to a list.
dfrtickers = pd.read_csv(strticker_list)
if dctFilters["GICS Sector"] is not None:
    dfrtickers = dfrtickers[dfrtickers["GICS Sector"] == dctFilters["GICS Sector"]]
if dctFilters["GICS Sub Industry"] is not None:
    dfrtickers = dfrtickers[dfrtickers["GICS Sub Industry"] == dctFilters["GICS Sub Industry"]]
if dctFilters["Symbol"] is not None:
    dfrtickers = dfrtickers[dfrtickers["Symbol"] == dctFilters["Symbol"]]
lsttickers = dfrtickers["Symbol"].to_list()

dfrdata_agg = None
# Could not use the direct Quandl call, since sending all 500 tickers casuses an error, most likely the url gets too long.
# So loop through tickers and append to existing dataframe.
for strticker in lsttickers:
    if dfrdata_agg is None:
        dfrdata_agg = stock_price_list(strticker, strstart_date, strend_date, strtoken)
    else:
        dfrdata_agg = dfrdata_agg.join(stock_price_list(strticker, strstart_date, strend_date, strtoken))
    print(strticker)
    # Sleep for 2 seconds so it doesn't hit the server so hard.
    sleep(2)

# Pivot dataframe so that each column is a constituent.
#dfrdata = dfrdata.pivot(index="date", columns="ticker", values="close")

dfrdata_agg.to_csv(strreport_path + "SPX_Prices_Tiingo_Financials_1990-2018.csv")