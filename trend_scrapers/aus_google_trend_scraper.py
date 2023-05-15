# %%
import pandas as pd
from pytrends.request import TrendReq
import datetime
import pytz

import json
import pathlib
import os 
pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

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


today = datetime.datetime.now()

scrape_date_stemmo = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y%m%d')

scrape_time = today.astimezone(pytz.timezone("Australia/Brisbane"))
format_scrape_time = datetime.datetime.strftime(scrape_time, "%Y_%m_%d_%H")

# %%

pytrend = TrendReq(hl='en-US', tz=360)

df = pytrend.trending_searches(pn='australia')
df.rename(columns={0: "Search"}, inplace=True)

df['scraped_datetime'] = format_scrape_time

# %%

zdf = df.copy()
zdf['Rank'] = zdf.index + 1

zdf = zdf[['Rank', 'Search']]

print(zdf)

# dumper('../archive/google', 'latest', zdf)

# dumper('../archive/google/daily_dumps', scrape_date_stemmo, zdf)

# with open(f'../static/latest_google.json', 'w') as f:
#     zdf.to_json(f, orient='records')


send_to_git(format_scrape_time, 'Archives', 'google', df)


# %%
