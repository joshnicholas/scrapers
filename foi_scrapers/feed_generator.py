# %%
import pandas as pd 

import os 
import pathlib

import datetime
import pytz

import json 
import time
from github import Github

pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

from dotenv import load_dotenv
load_dotenv()

# %%

today = datetime.datetime.now()
scrape_date_stemmo = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y%m%d')

selected_date = pd.date_range(today.date() - pd.to_timedelta(14, unit='d'), today, freq='D')

scrape_time = today.astimezone(pytz.timezone("Australia/Brisbane"))
format_scrape_time = datetime.datetime.strftime(scrape_time, "%Y_%m_%d_%H")
# print(selected_date)

# %%

tokeny = os.environ['gitty']

github = Github(tokeny)

repository = github.get_user().get_repo('Archives')

#### Get the inter files

def check_do(pathos):
    contents = repository.get_contents(pathos)
    # print(contents)
    fillos = [x.path.replace(f"{pathos}/", '') for x in contents]

    # print(fillos)
    return fillos


fillos = check_do(f'Archive/foi/inter')

listo = []

for fillo in fillos:
    if ".json" in fillo:
        inter = pd.read_json(f'https://raw.githubusercontent.com/joshnicholas/Archives/main/Archive/foi/inter/{fillo}')
        listo.append(inter)

# %%

cat = pd.concat(listo)
cat.drop_duplicates(subset=['Date', 'Agency', 'Id'])

cat['Date'] = pd.to_datetime(cat['Date'], format=['%Y-%m-%d'])
cat = cat.loc[cat['Date'].isin(selected_date)]

cat.sort_values(by=['Date'], ascending=False, inplace=True)

cat['Date'] = cat['Date'].dt.strftime('%Y-%m-%d')

cat.fillna('', inplace=True)

# print(cat)

jsony = cat.to_dict(orient='records')
content = json.dumps(jsony)

inter = f'Archive/foi/latest.json'

latters = repository.get_contents(inter)
repository.update_file(inter, f"updated_scraped_file_{format_scrape_time}", content, latters.sha)


# %%

# %%

# fillos = os.listdir('../archive/foi')
# fillos = [x for x in fillos if (".csv" in x) and ("latest" not in x)]

# print(fillos)

# listo = []
# for fillo in fillos:
#     inter = pd.read_csv(f'../archive/foi/{fillo}')
#     listo.append(inter)

# cat = pd.concat(listo)

# cat['Date'] = pd.to_datetime(cat['Date'], format='%Y-%m-%d')
# cat.sort_values(by=['Date'], ascending=False, inplace=True)
# cat['Date'] = cat['Date'].dt.strftime('%Y-%m-%d')

# cat.fillna('', inplace=True)

# # print(cat)
# # print(cat.columns.tolist())

# with open(f'../archive/foi/daily_dumps/{scrape_date_stemmo}.csv', 'w') as f:
#     cat.to_csv(f, index=False, header=True)

# with open(f'../archive/foi/latest.csv', 'w') as f:
#     cat.to_csv(f, index=False, header=True)

# with open(f'../static/latest_foi.json', 'w') as f:
#     cat.to_json(f, orient='records')


