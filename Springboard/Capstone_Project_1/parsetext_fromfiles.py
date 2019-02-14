
import pandas as pd
import re
import os.path
import html2text

"""
This module is used to parse out sentences that have certain keywords in them from files saved locally.

It has an exclusion list to try to remove false positives. The results are saved down in a csv.

"""

# Function to split text into sentences.
def split_into_lstsentences(strtext):
    alphabets= "([A-Za-z])"
    prefixes = "(Mr|St|Mrs|Ms|Dr|Prof|Capt|Cpt|Lt|Mt)[.]"
    suffixes = "(Inc|Ltd|Jr|Sr|Co)"
    starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
    acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
    websites = "[.](com|net|org|io|gov|me|edu)"
    
    strtext = " " + strtext + "  "
    strtext = strtext.replace("\n"," ")
    strtext = re.sub(prefixes,"\\1<prd>",strtext)
    strtext = re.sub(websites,"<prd>\\1",strtext)
    if "Ph.D" in strtext: strtext = strtext.replace("Ph.D.","Ph<prd>D<prd>")
    strtext = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",strtext)
    strtext = re.sub(acronyms+" "+starters,"\\1<stop> \\2",strtext)
    strtext = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",strtext)
    strtext = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",strtext)
    strtext = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",strtext)
    strtext = re.sub(" "+suffixes+"[.]"," \\1<prd>",strtext)
    strtext = re.sub(" " + alphabets + "[.]"," \\1<prd>",strtext)
    if "”" in strtext: strtext = strtext.replace(".”","”.")
    if "\"" in strtext: strtext = strtext.replace(".\"","\".")
    if "!" in strtext: strtext = strtext.replace("!\"","\"!")
    if "?" in strtext: strtext = strtext.replace("?\"","\"?")
    if "..." in strtext: strtext = strtext.replace("...","<prd><prd><prd>")
    if "e.g." in strtext: strtext = strtext.replace("e.g.","e<prd>g<prd>") 
    if "i.e." in strtext: strtext = strtext.replace("i.e.","i<prd>e<prd>")
    strtext = strtext.replace(".",".<stop>")
    strtext = strtext.replace("?","?<stop>")
    strtext = strtext.replace("!","!<stop>")
    strtext = strtext.replace("<prd>",".")
    lstsentences = strtext.split("<stop>")
    lstsentences = lstsentences[:-1]
    lstsentences = [s.strip() for s in lstsentences]
    return lstsentences

# Extracts a list of sentences from a larger list of text if certain keywords are found.  
# Does not include false positives by using an list of exclusion keywords.
def keywordsentences_extract(lstsentences, lstwords, lstexclustions):
    strsearch = "|".join(lstwords)
    strexclusions = "|".join(lstexclustions)
    strdigits = "[0-9,]{3}"
    lstresults = []
    for strsentence in lstsentences:
        if (re.search(strsearch, strsentence) is not None) and (re.search(strdigits, strsentence) is not None) and \
            (re.search(strexclusions, strsentence) is None) and len(strsentence) < 500:
            lstresults.append(strsentence)
    return lstresults

# Processes files saved locally to extract sentences based on certain keywords.
def parsetext_fromfile(strreport_path, strfile_name):
    with open(strreport_path + strfile_name, "r") as fletext:
        strtext = fletext.read()
        # Find where the first "document" within the file ends and redclare strtext to end there.
        strdoc_find = re.search("<\/DOCUMENT>", strtext)
        if strdoc_find is not None:
            strtext = strtext[0:strdoc_find.span()[1]]
        # Since many files might be HTML, convert all HTML files into pure text.
        strtext = html2text.html2text(strtext)
        lstsentences = split_into_lstsentences(strtext)
        lstresults = keywordsentences_extract(lstsentences, lstwords, lstexclustions)
        return lstresults

# Data local paths
strreport_path = "E:/EGDAR_10K/"
strticker_list = "M:/Code/Springboard/Capstone_Project_1/SPX_Constituents_2019-01-28.csv"
strreport_urls = "M:/Code/Springboard/Capstone_Project_1/Report_URLS_2019-01-28.csv"
strresults_path = "E:/Parse_Results_2019-01-28.csv"
dctFilters = {"GICS Sector": "Financials", "GICS Sub Industry": None, "Symbol": None, "Filename": None}
lstaggresults = []

# Keywords to search for.
lstwords = ["employ","employed","employs","employee","employees","full time","full\-time","fulltime"]
lstexclustions = ["401\(k\)","retire","retired","retirement","tax"]

# Read in the list of filenames from the reports.
dfrfilenames = pd.read_csv(strreport_urls)
dfrtickers = pd.read_csv(strticker_list)
dfrfilenames = dfrfilenames.merge(dfrtickers, how="left", left_on="ticker", right_on="Symbol")
dfrfilenames.insert(len(dfrfilenames.columns), "Results", "")

if dctFilters["GICS Sector"] is not None:
    dfrfilenames = dfrfilenames[dfrfilenames["GICS Sector"] == dctFilters["GICS Sector"]]
if dctFilters["GICS Sub Industry"] is not None:
    dfrfilenames = dfrfilenames[dfrfilenames["GICS Sub Industry"] == dctFilters["GICS Sub Industry"]]
if dctFilters["Symbol"] is not None:
    dfrfilenames = dfrfilenames[dfrfilenames["Symbol"] == dctFilters["Symbol"]]
if dctFilters["Filename"] is not None:
    dfrfilenames = dfrfilenames[dfrfilenames["filename"] == dctFilters["Filename"]]

# Loop through dataframe and process files.
for index, dfrrow in dfrfilenames.iterrows():
     lsttemp = parsetext_fromfile(strreport_path, dfrrow["filename"])
     dfrfilenames.at[index, "Results"] = lsttemp
     print(dfrrow["filename"])

dfrfilenames.to_csv(strresults_path)

