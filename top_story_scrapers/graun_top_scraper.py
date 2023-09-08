# %%
# import requests
import pandas as pd 
from bs4 import BeautifulSoup as bs 
import pytz
import datetime
import json
import requests
import re

import pathlib
import os 
pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

# %%
import time
from github import Github, UnknownObjectException

import boto3
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

r = requests.get("https://www.theguardian.com/au")


# %%

soup = bs(r.text, 'html.parser')
box = soup.find(id='container-most-viewed')
# print(box)
lister = box.find_all("li")


# # # print(r.text)
# items = [{"Headline":re.sub('\s+', ' ', x.h4.text.strip()), "Url": f"{x.a['href']}"} for x in items]
# # print(items)

# print(lister)

items = []

for thing in lister:
    record = {"Headline": re.sub('\s+', ' ', thing.h4.text.strip())}

    aye = thing.a['href']
    if "https://www.theguardian.com" in aye:
        record['Url'] = aye
    
    else:
        record['Url'] = "https://www.theguardian.com" + aye

        
    items.append(record)

# print(items)

# %%



df = pd.DataFrame(items)

df['scraped_datetime'] = format_scrape_time
df['publication'] = 'The Guardian'

# %%

zdf = df.copy()
zdf['Rank'] = zdf.index + 1

# print(zdf)

# print("Cols: ", zdf.columns.tolist())

# dumper('../archive/graun_top', 'latest', zdf)

# dumper('../archive/graun_top/daily_dumps', format_scrape_time, zdf)

# with open(f'../static/latest_graun_top.json', 'w') as f:
#     zdf.to_json(f, orient='records')

# %%

def send_to_s3(scrape_time, what, frame):
    yesterday = scrape_time - datetime.timedelta(days=1)
    twelve_ago = scrape_time - datetime.timedelta(hours=12)
    format_scrape_day = datetime.datetime.strftime(scrape_time, "%Y_%m_%d")
    format_scrape_yesterday = datetime.datetime.strftime(yesterday, "%Y_%m_%d")
    format_scrape_month = datetime.datetime.strftime(scrape_time, "%Y_%m")
    format_scrape_12_ago = datetime.datetime.strftime(twelve_ago, "%Y_%m_%d_%H")
    format_scrape_time = datetime.datetime.strftime(scrape_time, "%Y_%m_%d_%H")

    AWS_KEY = os.environ['awsykey']
    AWS_SECRET = os.environ['awsysec']

    session = boto3.Session(
            aws_access_key_id=AWS_KEY,
            aws_secret_access_key=AWS_SECRET,
            )

    s3 = session.resource('s3')
    s3_client = session.client('s3')
    my_bucket = s3.Bucket('chaluchasu')

    copier = frame.copy()
    copier.fillna('', inplace=True)

    jsony = copier.to_dict(orient='records')
    content = json.dumps(jsony)

    latest_path = f"{what}/latest.json"
    archive_path = f"{what}/dumps/{format_scrape_month}/{format_scrape_time}.json"

    print(archive_path)

    s3_client.put_object(
     Body=content,
     Bucket='chaluchasu',
     Key=latest_path
    )

    s3_client.put_object(
     Body=content,
     Bucket='chaluchasu',
     Key=archive_path
    )

    

send_to_s3(scrape_time, 'graun_top', zdf)


send_to_git(format_scrape_time, 'Archives', 'graun_top', zdf)


# %%
