# %%
import requests
session = requests.Session()

import pandas as pd 
import os
import json
import dateparser
import datetime
from dateutil.relativedelta import relativedelta
import pytz

from github import Github

from dotenv import load_dotenv
load_dotenv()

tokeny = os.environ['grauniad']

def rand_delay(num):
  import random 
  import time 
  rando = random.random() * num
#   print(rando)
  time.sleep(rando)

# pip3 install theguardian@git+https://github.com/prabhath6/theguardian-api-python.git

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

searcho = 'josh AND nicholas'

# https://content.guardianapis.com/search?q=12%20years%20a%20slave&format=json&tag=film/film,tone/reviews&from-date=2010-01-01&show-tags=contributor&show-fields=starRating,headline,thumbnail,short-url&order-by=relevance&api-key=test
# urlo = f"""https://content.guardianapis.com/search?q={searcho}&id=profile/josh-nicholas&query-fields=byline&format=json&show-tags=contributor&from-date=2020-01-01&show-fields=byline,headline,short-url&order-by=relevance&api-key={tokeny}"""
urlo = f"""https://content.guardianapis.com/search?q={searcho}&id=profile/josh-nicholas&query-fields=byline&format=json&from-date=2019-01-01&show-fields=byline,body,headline&order-by=newest&api-key={tokeny}"""


r = requests.get(urlo)


# %%


jsony = json.loads(r.text)

num_pages = jsony['response']['pages']
# print("Pages: ", num_pages)

# print(jsony)

filtered = []

for page in range(1, num_pages+1):
# for page in range(1, 2):
    print("Starting page: ", page)
    new_r = session.get(urlo, params={'page': page})
    new_jsony = json.loads(new_r.text)
    rand_delay(2)

    listo = new_jsony['response']['results']

    for thingo in listo:
        # print(thingo['fields'])
        # print(thingo['tags'])
        byline = thingo['fields']['byline']
        if "Josh Nicholas" in byline:
            filtered.append(thingo)

# print(filtered[0])

# %%


cat = pd.DataFrame.from_records(filtered)


send_to_git(format_scrape_time, 'Archives', 'journalism', cat)
# %%

