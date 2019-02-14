Capstone Project 1
------------------

The code is laid out in the following manner:
SPX_Constituents_2019-01-28.csv		List of SPX constituents as of January 2019.
edgarpull.py 				Pulls 10-K reports from the SEC EDGAR website and save them locally based on stock tickers. 
					It can be configured to pull other types as well, the filters just need to be set properly.
Report_URLS_2019_01-28.csv 		Record of companies, URLs, and filenames that were processed.
BLK_2017-02-28_0001564590-17-002816.txt	Sample of 10-K file for BlackRock YE 2017.
BLK_2018-02-28_0001564590-18-003744.txt	Sample of 10-K file for BlackRock YE 2018.
parsetext_from_files.py - 		Looks for first document in the multi-document 10-K local file. Converts files from HTML to text.
					Breaks up the document into sentences and then looks for sentences with keywords, excluding sentences
					with other keywords to remove false positives.
Parse_Results_2019-01-28.csv		Currently contains pre-finalized results from the processing of 10-K files, looking for employee counts.
					Sentences have been identified with keywords, now just need to pull out relevant numeric information.
stock_price_pull.py			Uses Quandl package to pull stock prices for a specific list of tickers.
SPX_Prices_1990-2018.csv		Results of Quandl download, stock prices for SPX constituents.