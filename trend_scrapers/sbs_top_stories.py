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

        print(pathos)
        print("contents: ", contents)
        print("fillos: ", fillos)
        return fillos


    # latest_donners = check_do(f'Archive/{what}')
    donners = check_do(f'Archive/{what}/daily_dumps')

    latters = repository.get_contents(latest)
    repository.update_file(latest, f"updated_scraped_file_{stemmo}", content, latters.sha)

    if f"{stemmo}.json" not in donners:

        repository.create_file(filename, f"new_scraped_file_{stemmo}", content)

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


r = requests.get("https://www.sbs.com.au/news/collection/top-stories", headers=headers)


# start_url = "https://www.sbs.com.au/news/collection/top-stories"
# driver.get(start_url)



# %%


soup = bs(r.text, 'html.parser')
div = soup.find("div", {"data-layer-event-source-title":"Top Stories"})


items = div.find_all("a", {"data-testid":"internal-link"})
items = [x for x in items if x.find('h2')]

print(items[:2])
counter = 1

sent = 0

records = []

for thing in items:

    try:

        heado = thing.h2.text

        # print(heado)

        linko = thing['href']
        linko = 'https://www.sbs.com.au' + linko
        # print(linko)

        dicto = {"publication": "SBS",

        'scraped_datetime': format_scrape_time,
        'Headline': heado.replace("analysis:", '').strip(),
        'Url': linko.strip(),
        'Rank': counter
        }

        counter += 1

        records.append(dicto)

    except Exception as e:

        print(f"Exception is {e}")
        print(f"Line: {sys.exc_info()[-1].tb_lineno}")
        continue




df = pd.DataFrame.from_records(records)

# print(df)
# print(df.columns.tolist())

send_to_git(format_scrape_time, 'Archives', 'sbs_top', df)

# %%
