# %%
import requests
import pandas as pd 
from bs4 import BeautifulSoup as bs 
import pytz
import datetime
import json

import pathlib
import os 
pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

import time
from github import Github

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


r = requests.get("https://www.abc.net.au/news/", headers=headers)


# %%

soup = bs(r.text, 'html.parser')
div = soup.find("div", {"data-uri":"recommendation://collection/abc-news-homepage-sidebar"})
# recommendation://collection/abc-news-homepage-sidebar
items = div.find_all("a", {"data-component":"Link"})

# print(items)

# %%

# %%

counter = 1

sent = 0

records = []

for thing in items:

    heado = thing.text

    urlo = 'https://www.abc.net.au' + thing['href']

    dicto = {"publication": "ABC",

    'scraped_datetime': format_scrape_time,
    'Headline': heado.replace("analysis:", '').strip(),
    'Url': urlo.strip(),
    'Rank': counter
    }

    counter += 1

    records.append(dicto)

# %%

df = pd.DataFrame.from_records(records)

# dumper('../archive/abc_top', 'latest', df)

# dumper('../archive/abc_top/daily_dumps', format_scrape_time, df)

# with open(f'../static/latest_abc_top.json', 'w') as f:
#     df.to_json(f, orient='records')

print(df)





send_to_git(format_scrape_time, 'Archives', 'abc_top', df)

# %%
