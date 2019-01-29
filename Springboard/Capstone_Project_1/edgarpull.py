import requests
from requests_html import HTMLSession
import pandas as pd
import re
import os.path
from time import sleep

"""
This module is used to pull SEC EDGAR 10-K files for a list of companies
and save them to a local hard drive.

It is then used process those saved 10-K files and extract
specific data.

"""
# Processes a list of tickers and gets underlying report type urls.
def EDGAR_report_list(lsttickers, strrpt_type):
    # Use requests-HTML to request page and traverse to correct HTML tags.
    htsSEC = HTMLSession()
    lstreports = []

    # Create dictionary of arguement strings that can be used to query documents from EDGAR site.
    dctargs = {}
    dctargs["url"] = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&dateb=&owner=exclude&count=100"
    dctargs["type"] = "&type="
    dctargs["ticker"]= "&CIK="

    # Loop through each ticker in list.
    for ticker in lsttickers:
        # Construct and send url.
        strrequest_url = dctargs["url"]
        strrequest_url += dctargs["type"] + strrpt_type
        strrequest_url += dctargs["ticker"] + ticker
        response = htsSEC.get(strrequest_url)
        # Check if request succeeded.
        if response.status_code == 200: # Standard response for successful HTTP requests.
            lstresults = response.html.xpath("//table[@summary='Results']/tr")
            lstreports += EDGAR_results_parse(lstresults, ticker)
        else:
            print("Failure occurred for company %s report type %s." % (ticker, strrpt_type))
        # Sleep for 3 seconds so it doesn't hit the server so hard.
        sleep(3)
    return lstreports

# Parses out urls from results page for each ticker.
def EDGAR_results_parse(lstresults, ticker):
    lstreports = []
    
    # Loop through the list of results which is a html table, so going through tr/td tags.
    for htrresult in lstresults:
        if len(htrresult.xpath("//td")) > 0:
            # Create dictionary and store information.
            dctreport = {}
            dctreport["ticker"] = ticker
            dctreport["docurl"] = htrresult.xpath("//a[@id='documentsbutton']/@href")[0]
            # Get where the CIK ID ends in the URL so a full url can be created later.
            intindex = re.search(r'data\/[0-9]+\/', dctreport["docurl"]).span()[1]
            dctreport["path"] = "https://www.sec.gov" + dctreport["docurl"][0:intindex]
            # Get only the account number since it is used in the url construction.
            stracctno = re.search(r'Acc-no: [0-9\-]+', htrresult.xpath("//td[3]")[0].text)[0]
            stracctno = stracctno.replace("Acc-no: ", "")
            dctreport["desc"] = stracctno
            dctreport["filedate"] = htrresult.xpath("//td[4]")[0].text
            # Construct full path to report complete submission html/text file.
            dctreport["path"] += dctreport["desc"].replace("-", "") + "/" +dctreport["desc"] + ".txt"
            lstreports.append(dctreport)
    return lstreports

# Saves files from a list of urls down to a specified path.
def web_file_download(strpath, lsturls, lstfile_name):
    # Loop through the urls and associated file names.
    for strurl, strfile_name in zip(lsturls, lstfile_name):
        # Send a request to get the file and then save it down to the file path.
        response = requests.get(strurl)
        strfile_text = response.content
        with open(strreport_path + strfile_name,"w+b") as flereport:
            flereport.write(strfile_text)
        sleep(2)

# Data local paths
strreport_path = "E:/EGDAR_10K/"
strticker_list = "M:/Code/Springboard/Capstone_Project_1/SPX_Constituents_2019-01-28.csv"
strreport_urls = "M:/Code/Springboard/Capstone_Project_1/Report_URLS_2019-01-28.csv"

# Check if file of urls has already been created. If so, no need to reprocess.
if not os.path.isfile(strreport_urls):
    # Pull stock tickers from CSV file.
    dfrtickers = pd.read_csv(strticker_list)

    # Store information in dataframe and then export to csv.
    lstreports = EDGAR_report_list(dfrtickers["Symbol"], "10-K")
    dfrreports = pd.DataFrame(lstreports)
    dfrreports.to_csv(strreport_urls)
else:
    dfrreports = pd.read_csv(strreport_urls)

# Load all the 10-K text files
dfrreports["filename"] = dfrreports["ticker"] + "_" + dfrreports["filedate"] + "_" + dfrreports["desc"] + ".txt"
dfrreports.to_csv(strreport_urls)
web_file_download(strreport_path, dfrreports["path"], dfrreports["filename"])