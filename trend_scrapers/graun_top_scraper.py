# %%
# import requests
import pandas as pd 
from bs4 import BeautifulSoup as bs 
import pytz
import datetime
import json
import requests

import pathlib
import os 
pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

# %%

# %%

def dumper(path, name, frame):
    with open(f'{path}/{name}.csv', 'w') as f:
        frame.to_csv(f, index=False, header=True)


# %%

today = datetime.datetime.now()

scrape_date_stemmo = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y%m%d')

scrape_time = today.astimezone(pytz.timezone("Australia/Brisbane"))
format_scrape_time = datetime.datetime.strftime(scrape_time, "%Y_%m_%d_%H")


headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
'Accept-Language': "en-GB,en-US;q=0.9,en;q=0.8",
"Referer": 'https://www.google.com',
"DNT":'1'}

# %%

r = requests.get("https://www.theguardian.com/au")
soup = bs(r.text, 'html.parser')
items = soup.find_all("li", class_="most-popular__item")


items = [{"Headline":f"{x.h3.text.strip()}", "Url": f"{x.a['href']}"} for x in items]


# print(items)

df = pd.DataFrame(items)

df['scraped_datetime'] = scrape_time

# %%

zdf = df.copy()
zdf['Rank'] = zdf.index + 1


dumper('../archive/graun_top', 'latest', zdf)

dumper('../archive/graun_top/daily_dumps', format_scrape_time, zdf)

with open(f'../static/latest_graun_top.json', 'w') as f:
    zdf.to_json(f, orient='records')

