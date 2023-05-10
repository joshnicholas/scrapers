# %%
import pandas as pd 

import os 
import pathlib

import datetime
import pytz

pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

# %%

today = datetime.datetime.now()
scrape_date_stemmo = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y%m%d')

# %%

fillos = os.listdir('../data/foi')
fillos = [x for x in fillos if ".csv" in x]

# print(fillos)

listo = []
for fillo in fillos:
    inter = pd.read_csv(f'../data/foi/{fillo}')
    listo.append(inter)

cat = pd.concat(listo)

cat['Date'] = pd.to_datetime(cat['Date'], format='%Y-%m-%d')
cat.sort_values(by=['Date'], ascending=False, inplace=True)
cat['Date'] = cat['Date'].dt.strftime('%Y-%m-%d')

cat.fillna('', inplace=True)

# print(cat)
# print(cat.columns.tolist())

with open(f'../archive/foi/daily_dumps/{scrape_date_stemmo}.csv', 'w') as f:
    cat.to_csv(f, index=False, header=True)

with open(f'../archive/foi/latest_foi.csv', 'w') as f:
    cat.to_csv(f, index=False, header=True)

with open(f'../static/latest_foi.json', 'w') as f:
    cat.to_json(f, orient='records')


