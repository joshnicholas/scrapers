# %%
# import requests
import pandas as pd 
from bs4 import BeautifulSoup as bs 
import pytz
import datetime
import json

import pathlib
import os 
pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

# %%

from selenium import webdriver 
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")


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


driver = webdriver.Chrome(options=chrome_options)
start_url = "https://smh.com.au"
driver.get(start_url)

# import requests

# r = requests.get('https://www.smh.com.au/national', headers=headers)

# %%

soup = bs(driver.page_source.encode("utf-8"), 'html.parser')

# print(r.text)

# print(soup)

# %%

container = soup.find("section", {"data-an-name": "Most Popular"})

# print(container)
items = container.find_all("h3")
# print(items)


items = [{"SMH most viewed":f"{x.text.strip()}", "Url": f"{'https://www.smh.com.au' + x.a['href']}"} for x in items]

df = pd.DataFrame(items)

# print(df)

# %%

zdf = df.copy()
zdf['Rank'] = zdf.index + 1

print(zdf)
# %%

dumper('../archive/smh_top', 'latest', zdf)

dumper('../archive/smh_top/daily_dumps', scrape_date_stemmo, zdf)

with open(f'../static/latest_smh_top.json', 'w') as f:
    zdf.to_json(f, orient='records')

# %%
