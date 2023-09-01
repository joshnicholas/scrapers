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
# from selenium.webdriver.chrome.options import Options
# chrome_options = Options()
# chrome_options.add_argument("--headless")


from selenium.webdriver.chrome.service import Service
service = Service()
options = webdriver.ChromeOptions()
options.add_argument("--headless")

driver = webdriver.Chrome(service=service, options=options)

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

start_url = "https://www.news.com.au/"
driver.get(start_url)

soup = bs(driver.page_source.encode("utf-8"), 'html.parser')

# %%

print(soup)

# container = soup.find("div", class_="most-pop-item")
# items = container.find_all("li")
# items = [{"News most viewed":f"{x.text.strip()}"} for x in items]

# df = pd.DataFrame(items)

# df = df.T.reset_index()
# headers = [f"{x}" for x in range(0,10)]
# headers.insert(0, "What")
# df.columns = headers

# %%

# print(df)

# %%
