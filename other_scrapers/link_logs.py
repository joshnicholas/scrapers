# %%
import requests
session = requests.Session()

import pandas as pd 
import os
import json
import dateparser
import datetime
# from dateutil.relativedelta import relativedelta
import pytz

from github import Github
import feedparser
from dotenv import load_dotenv
load_dotenv()

# %%
today = datetime.datetime.now()

scrape_date_stemmo = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y%m%d')

scrape_time = today.astimezone(pytz.timezone("Australia/Brisbane"))
format_scrape_time = datetime.datetime.strftime(scrape_time, "%Y_%m_%d_%H")

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
        



# %%

# %%

urlo = 'https://joshnicholas.blog/categories/linklog/feed.xml'

# %%
d = feedparser.parse(urlo)

listo = []
for entry in d['entries']:
    # print(entry)
    entry = dict((k, v) for k, v in entry.items() if v)

    listo.append(entry)

cat = pd.DataFrame.from_records(listo)

# print(cat)

# %%
send_to_git(format_scrape_time, 'Archives', 'link-log', cat)