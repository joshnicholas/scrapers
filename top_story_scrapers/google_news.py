# %%

import pandas as pd
import requests
import datetime
import pytz
import pathlib
import os 
pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

from gnews import GNews
from dotenv import load_dotenv
load_dotenv()

from github import Github, UnknownObjectException
import json
import boto3
from dotenv import load_dotenv
load_dotenv()

# %%

today = datetime.datetime.now()
scrape_date_stemmo = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y%m%d')
scrape_hour = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%H')

scrape_time = today.astimezone(pytz.timezone("Australia/Brisbane"))
format_scrape_time = datetime.datetime.strftime(scrape_time, "%Y_%m_%d_%H")

utc_now = datetime.datetime.utcnow()
utc_then = utc_now - datetime.timedelta(days=1)

utc_month = datetime.date.strftime(utc_then, '%m')
utc_year = datetime.date.strftime(utc_then, '%Y')
utc_day = datetime.date.strftime(utc_then, '%d')

utc_reverse_date = utc_then.strftime('%Y-%m-%d')
utc_hour = utc_then.strftime('%H')

# %%

google_news = GNews(language='en', country='AU', period='2h')
# aus_news = google_news.get_news('Australia')
aus_news = google_news.get_top_news()

# %%
records = []
for thingo in aus_news:
    record = {"Headline": thingo['title'], "Url": thingo['url'], 'publication': thingo['publisher']['title'],
              "Publish datetime": thingo['published date']}
    records.append(record)

# %%


df = pd.DataFrame.from_records(records)
df['scraped_datetime'] = format_scrape_time
df['Rank'] = df.index + 1

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

    # print(archive_path)

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

    

send_to_s3(scrape_time, 'google_top', df)

send_to_git(scrape_date_stemmo, 'Archives', 'google_top', df)