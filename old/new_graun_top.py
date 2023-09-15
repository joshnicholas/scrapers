# %%
# import requests
import pandas as pd 
from bs4 import BeautifulSoup as bs 
import pytz
import datetime
import json
import requests
import re
import requests

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


# %%

today = datetime.datetime.now()

scrape_date_stemmo = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y%m%d')

scrape_time = today.astimezone(pytz.timezone("Australia/Brisbane"))
format_scrape_time = datetime.datetime.strftime(scrape_time, "%Y_%m_%d_%H")


# %%



headers = {
    'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
    'Referer': 'https://www.theguardian.com/media/2023/sep/15/chris-kenny-cops-it-from-his-readers-for-sticking-by-the-voice',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    'sec-ch-ua-platform': '"macOS"',
}

params = {
    'dcr': 'true',
}

response = requests.get('https://api.nextgen.guardianapps.co.uk/most-read-geo.json', params=params, headers=headers)


# %%

items = []

jsony = json.loads(response.text)
# 'country', 'heading', 'trails'

# dict_keys(['url', 'linkText', 'showByline', 'byline', 
#            'masterImage', 'image', 'carouselImages', 
#            'isLiveBlog', 'pillar', 'designType', 'format', 
#            'webPublicationDate', 'headline', 'shortUrl', 
#            'discussion'])

rank = 1
for thingo in jsony['trails']:
    record = {'Headline': thingo['linkText'],
              "Url": thingo['linkText'],
              "publication": "The Guardian",
              "Rank": rank,
              "scraped_datetime": format_scrape_time,
              "Publish datetime":thingo['webPublicationDate'],
              'isLiveBlog':thingo['isLiveBlog']}

    rank += 1
    items.append(record)

    # print(record)

df = pd.DataFrame(items)

print(df)

# ['Headline', 'Url', 'scraped_datetime', 'publication', 'Rank']
# 
# print(jsony['trails'][0]['isLiveBlog'])
# %%
