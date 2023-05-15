# %%
import pandas as pd 

import requests
from bs4 import BeautifulSoup as bs

from dateparser.search import search_dates
import datetime 
import pytz
import sys

import os 
import pathlib

today = datetime.datetime.now()
scrape_date_stemmo = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y%m%d')
scrape_time = today.astimezone(pytz.timezone("Australia/Brisbane"))
format_scrape_time = datetime.datetime.strftime(scrape_time, "%Y_%m_%d_%H")

import json 
import time
from github import Github

# %%

agency = 'services'

def send_foi_to_git(stemmo, repo, what, agent, frame):

    tokeny = os.environ['gitty']

    github = Github(tokeny)

    repository = github.get_user().get_repo(repo)

    jsony = frame.to_dict(orient='records')
    content = json.dumps(jsony)

    filename = f'Archive/{what}/daily_dumps/{stemmo}.json'

    inter = f'Archive/{what}/inter/{agent}.json'

    def check_do(pathos):
        contents = repository.get_contents(pathos)

        fillos = [x.path.replace(f"{pathos}/", '') for x in contents]

        print(pathos)
        print("contents: ", contents)
        print("fillos: ", fillos)
        return fillos

    donners = check_do(f'Archive/{what}/daily_dumps')

    latters = repository.get_contents(inter)
    repository.update_file(inter, f"updated_scraped_file_{stemmo}", content, latters.sha)

    if f"{stemmo}.json" not in donners:

        repository.create_file(filename, f"new_scraped_file_{stemmo}", content)
    

#%%

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
'Accept-Language': "en-GB,en-US;q=0.9,en;q=0.8",
"Referer": 'https://www.google.com',
"DNT":'1'}

urlo = 'https://www.servicesaustralia.gov.au/freedom-information-disclosure-log'
home = urlo
r = requests.get(urlo, headers=headers)

soup = bs(r.text, 'html.parser')


# %%


rows = soup.find_all('tr')

listo = []

for row in rows[1:5]:

    # print(row)

    try:

        stringo = row.text
        # print(stringo)

        datter = search_dates(stringo)
        datto = datetime.datetime.strptime(datter[0][0], "%d %B %Y")
        use_date = datto.strftime("%Y-%m-%d")



        title = row.find_all('p')[0].text.strip()
        # print(title)

        file = 'https://www.servicesaustralia.gov.au/freedom-information-disclosure-log' 

        record = {"Agency": "Services Australia",
                "Date": use_date,
                "Id":title.replace(" ", '').strip().lower(), 
                "Title": title,
                "Url": urlo,
                "Home_url": home,
                "File": file}
        print(record)
        listo.append(record)

    except Exception as e:

        print(urlo)
        print(f"Exception is {e}")
        print(f"Line: {sys.exc_info()[-1].tb_lineno}")
        continue



    
# %%

cat = pd.DataFrame.from_records(listo)

send_foi_to_git(f"{format_scrape_time}_{agency}", 'Archives', 'foi', agency, cat)
# %%
