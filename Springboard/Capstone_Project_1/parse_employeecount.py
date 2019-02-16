import pandas as pd
import numpy as np
from datetime import datetime
import re

"""
This module is used to parse out the employee counts within the pre-parsed out sentences stored in the dataframe.
It iterates through a list of patterns to fill in the column.

"""

# Function to search through the sentences that match having a year and employee type text using a list of patterns.
def extract_employees(lstsearch_text, strsearch_year, lstsentences):

    # Use a waterfall of criteria to run through the list of sentences completely before moving on to the next one.
    # If something is found earlier in the waterfall, the return statement will exit the functions anyway.
    # Run through the list of search texts using the previous year.
    for strsentence in lstsentences:
        for strsearch_text in lstsearch_text:
            if (re.search(strsearch_text, strsentence) is not None) and (re.search(strsearch_year, strsentence) is not None):
                strmatch = re.search(strsearch_text, strsentence).group(0)
                strmatch = re.search("[0-9,]*[0-9]", strmatch).group(0)
                return [strsearch_year, int(strmatch.replace(",", ""))]
    # Run through the list of search texts using the current year, which is less likely.
    for strsentence in lstsentences:
        for strsearch_text in lstsearch_text:
            strsearch_year_temp = str(int(strsearch_year) + 1) # Advance back to current year.
            if (re.search(strsearch_text, strsentence) is not None) and (re.search(strsearch_year_temp, strsentence) is not None):
                strmatch = re.search(strsearch_text, strsentence).group(0)
                strmatch = re.search("[0-9,]*[0-9]", strmatch).group(0)
                return [strsearch_year_temp, int(strmatch.replace(",", ""))]
    # Run through the list of search texts without using any year, which is least likely to be accurate.
    for strsentence in lstsentences:
        for strsearch_text in lstsearch_text:
            if re.search(strsearch_text, strsentence) is not None:
                strmatch = re.search(strsearch_text, strsentence).group(0)
                strmatch = re.search("[0-9,]*[0-9]", strmatch).group(0)
                return [strsearch_year, int(strmatch.replace(",", ""))]
            

lstpatterns = ["[0-9,]*[0-9] full- time", "[0-9,]*[0-9] full-time","[0-9,]*[0-9] full time",
               "was [0-9,]*[0-9], all of whom were employed",
               "[0-9,]*[0-9] employees","[0-9,]*[0-9] individuals","[0-9,]*[0-9] people",
               "[0-9,]*[0-9] associates","[0-9,]*[0-9] persons", "[0-9,]*[0-9] active, full-time equivalent",
               "Full-time equivalent \(""FTE""\) employees totaled [0-9,]*[0-9]", "Full-time equivalent employees totaled [0-9,]*[0-9]", 
               "We have approximately [0-9,]*[0-9] employees", "We have [0-9,]*[0-9] average full-time equivalent employees",
               "we had [0-9,]*[0-9] total staff", 
               "number of full-time equivalent employees of Moody\x92s was approximately [0-9,]*[0-9].",
               "The number of employees, excluding temporary employees, at \w+ \d+, \d+, was [0-9,]*[0-9]"
               "[0-9,]*[0-9]/* employees", "Average full-time equivalent employees totaled approximately [0-9,]*[0-9]",
               "and employed [0-9,]*[0-9]", "Active full-time equivalent employees totaled [0-9,]*[0-9] at year-end"]


strresults_path = "M:/Code/Springboard/Capstone_Project_1/Capstone_Project_1/Parse_Results_2019-01-28.csv"
dfrdata = pd.read_csv(strresults_path)

# Do column clean up, creating the columns needed for later storage of results if they don't exist.
dfrdata = dfrdata.drop(columns="Unnamed: 0")
if "EmpCount" not in dfrdata.columns:
    dfrdata.insert(len(dfrdata.columns)-1, "EmpCount", "")
if "RptYear" not in dfrdata.columns:
    dfrdata.insert(len(dfrdata.columns)-1, "RptYear", "")
dfrdata = dfrdata.fillna("")

# Set this flag if you want to reprocess all records rather than just incrementally update the missing ones.
blnreprocess = False

for index, dfrrow in dfrdata.iterrows():
    if blnreprocess or dfrrow["EmpCount"] == "":
        lstsentences = dfrrow["Results"]
        if lstsentences != "" and lstsentences != "[]":
            print(dfrrow["filename"])
            lstsentences = pd.eval(lstsentences)
            strsearch_year = str(datetime.strptime(dfrrow["filedate"], "%m/%d/%Y").year - 1)
            lstresult = extract_employees(lstpatterns, strsearch_year, lstsentences)
            if lstresult is not None:
                dfrdata.at[index, "RptYear"] = lstresult[0]
                dfrdata.at[index, "EmpCount"] = lstresult[1]


dfrdata.to_csv("M:/Code/Springboard/Capstone_Project_1/Capstone_Project_1/Parse_Results_2019-01-28.csv")