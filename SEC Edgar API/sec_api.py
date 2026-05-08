#import modules
import requests
import pandas as pd

#create request header
headers = {'User-Agent': 'chancuadero22@gmail.com'}

#get all companies data
companyTickers = requests.get("https://www.sec.gov/files/company_tickers.json", headers=headers)


#format response to dictionary and get first key/value
firstEntry = companyTickers.json().values()
cik_str = []

for cik in firstEntry:
    extract_cik = str(cik['cik_str'])
    format_cik = extract_cik.zfill(10)
    cik_str.append(format_cik)

print(cik_str[:10])