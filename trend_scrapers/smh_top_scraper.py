# %%
# import requests
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

from dotenv import load_dotenv
load_dotenv()

# %%

from selenium import webdriver 
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")
# chrome_options.add_argument('--no-sandbox') 
driver = webdriver.Chrome(options=chrome_options)

import time
from github import Github, UnknownObjectException

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

    def try_file(pathos):
        try:
            repository.get_contents(pathos)
            return True
        except UnknownObjectException as e:
            return False

    # latest_donners = check_do(f'Archive/{what}')
    # donners = check_do(f'Archive/{what}/daily_dumps')
    donners = try_file(filename)

    latters = repository.get_contents(latest)
    repository.update_file(latest, f"updated_scraped_file_{stemmo}", content, latters.sha)

    if donners == False:

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

try:

    # print(container)
    items = container.find_all("h3")
    # print(items)


    items = [{"Headline":f"{x.text.strip()}", "Url": f"{'https://www.smh.com.au' + x.a['href']}"} for x in items]

    df = pd.DataFrame(items)

    df['scraped_datetime']= format_scrape_time 
    df['publication'] = 'SMH'

    # print(df)

    # %%

    zdf = df.copy()
    zdf['Rank'] = zdf.index + 1

    # print(zdf)
    # %%

    # dumper('../archive/smh_top', 'latest', zdf)

    # dumper('../archive/smh_top/daily_dumps', format_scrape_time, zdf)

    # with open(f'../static/latest_smh_top.json', 'w') as f:
    #     zdf.to_json(f, orient='records')

    send_to_git(format_scrape_time, 'Archives', 'smh_top', zdf)

    # %%

except Exception as e:

    print(f"Exception is {e}")
    print(f"Line: {sys.exc_info()[-1].tb_lineno}")


