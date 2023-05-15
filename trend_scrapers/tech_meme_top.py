# %%
import requests
import pandas as pd 
from bs4 import BeautifulSoup as bs 
import pytz
import datetime
import json

import sys

import pathlib
import os 
pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

from selenium import webdriver 
from selenium.webdriver.chrome.options import Options

# chrome_options = Options()
# chrome_options.add_argument("--headless")
# # chrome_options.add_argument('--no-sandbox') 
# driver = webdriver.Chrome(options=chrome_options)

import time
from github import Github

from dotenv import load_dotenv
load_dotenv()

# %%

def send_to_git(stemmo, repo, what, frame):

    tokeny = os.environ['gitty']

    github = Github(tokeny)

    repository = github.get_user().get_repo(repo)

    jsony = frame.to_dict(orient='records')
    content = json.dumps(jsony)

    filename = f'Archive/{what}/daily_dumps/{stemmo}.json'
    latest = f'Archive/{what}/latest.json'

    def check_do(pathos):
        contents = repository.get_contents(pathos)

        fillos = [x.path.replace(f"{pathos}/", '') for x in contents]

        # print(pathos)
        # print("contents: ", contents)
        # print("fillos: ", fillos)
        return fillos


    # latest_donners = check_do(f'Archive/{what}')
    donners = check_do(f'Archive/{what}/daily_dumps')

    latters = repository.get_contents(latest)
    repository.update_file(latest, f"updated_scraped_file_{stemmo}", content, latters.sha)

    if f"{stemmo}.json" not in donners:

        repository.create_file(filename, f"new_scraped_file_{stemmo}", content)


today = datetime.datetime.now()

scrape_date_stemmo = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y%m%d')

scrape_time = today.astimezone(pytz.timezone("Australia/Brisbane"))
format_scrape_time = datetime.datetime.strftime(scrape_time, "%Y_%m_%d_%H")


headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
'Accept-Language': "en-GB,en-US;q=0.9,en;q=0.8",
"Referer": 'https://www.google.com',
"DNT":'1'}

# %%

r = requests.get("https://www.techmeme.com/")

soup = bs(r.text, 'html.parser')

container = soup.find("div", {"id": "topcol1"})
divs = container.find_all("div", class_="clus")



# %%

# print(divs[0])

items = [{"Headline":f"{div.find('strong').text.strip()}", "Url": f"{div.find(class_='ourh')['href'].strip()}"} for div in divs]
# print(items)
# %%

df = pd.DataFrame.from_records(items)

df['Rank'] = df.index + 1

df['scraped_datetime'] = format_scrape_time

# print(df)
# %%

send_to_git(format_scrape_time, 'Archives', 'tech_meme_top', df)