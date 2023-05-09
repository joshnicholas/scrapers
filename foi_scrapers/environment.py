# %%
import pandas as pd 

import requests
from bs4 import BeautifulSoup as bs

import datetime 
import pytz
import sys

import os 
import pathlib

# %%

##
def dumper(path, name, frame):
    with open(f'{path}/{name}.csv', 'w') as f:
        frame.to_csv(f, index=False, header=True)

##
def rand_delay(num):
  import random 
  import time 
  rando = random.random() * num
  print(rando)
  time.sleep(rando)

def already_done(pathos, stemmo):

    if pathos[-1] != '/':
        pathos += '/'

    if f'{stemmo}.csv' in os.listdir(pathos):
        inter = pd.read_csv(f"{pathos}{stemmo}.csv")
        uniques = inter['Id'].unique().tolist()
        return uniques
    else:
        return []

def create_raw_append_csv(pathos, nammo, new_record, drop_col, sort_col):

    new = pd.DataFrame.from_records([new_record])

    if pathos[-1] != '/':
        pathos += '/'
    # print("cwd:", os.getcwd())
    fillos = os.listdir(pathos)
    # print(fillos)
    if f'{nammo}.csv' not in fillos:
        # print("if")
        dumper(pathos, nammo, new)
    
    else:
        # print("else")
        old = pd.read_csv(f"{pathos}{nammo}.csv")

        tog = pd.concat([new, old])
        tog.drop_duplicates(subset=[drop_col], inplace=True)
        tog.sort_values(by=[sort_col], ascending=False, inplace=True)
        
        dumper(pathos, nammo, tog)
    

# %%

pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

# print("cwd:", os.getcwd())

#%%

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
'Accept-Language': "en-GB,en-US;q=0.9,en;q=0.8",
"Referer": 'https://www.google.com',
"DNT":'1'}

urlo = 'https://www.dcceew.gov.au/about/reporting/freedom-of-information/disclosure-log'
home = urlo
r = requests.get(urlo, headers=headers)

soup = bs(r.text, 'html.parser')


# %%

rows = soup.find_all('tr')

donners = already_done('../data/foi', 'treasury')
# print("donners: ", donners)

for row in rows[1:]:

    # print(row)

    try:

        stemmo = row.find(attrs={"headers":"view-field-reference-table-column"}).text.strip()
        # print(stemmo)

        if stemmo not in donners:
        
            datto = row.find(class_='datetime').text.strip()
            datto = datetime.datetime.strptime(datto, "%d %B %Y")
            datto = datto.strftime("%Y-%m-%d")
            # print(datto)

            title = row.find(attrs={"headers":"view-field-summary-table-column"}).text.strip()
            # print(title)

            # urlo = row.find(attrs={"headers":"view-title-table-column"}).a['href']
            urlo = row.find(class_='file--application-pdf').a['href']
            # print(urlo)

            file = 'https://www.dcceew.gov.au/' + urlo
            # print(file)

            record = {"Agency": "Environment",
                    "Date": datto,
                    "Id": stemmo,
                    "Title": title,
                    "Url": urlo,
                    "Home_url": home,
                    "File": file}
            
            # print(record)
            create_raw_append_csv('../data/foi', 'environment', record, "Id", 'Date')

    except AttributeError as e:

        print(urlo)
        print(f"Exception is {e}")
        print(f"Line: {sys.exc_info()[-1].tb_lineno}")
        continue


# print(rows[1])
# %%
# https://www.dcceew.gov.au/about/reporting/freedom-of-information/disclosure-log#:~:text=Environment%20and%20Water-,72528.pdf,-72894