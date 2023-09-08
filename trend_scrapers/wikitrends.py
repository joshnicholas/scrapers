# %%
import pandas as pd
import requests
import datetime
import json
import requests

import time 

import pytz
import pathlib
import os 
pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

import time
from github import Github, UnknownObjectException

from dotenv import load_dotenv
load_dotenv()

# %%

def send_to_s3(scrape_time, what, frame):
    import boto3
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
scrape_hour = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%H')

scrape_time = today.astimezone(pytz.timezone("Australia/Brisbane"))
format_scrape_time = datetime.datetime.strftime(scrape_time, "%Y_%m_%d_%H")

utc_now = datetime.datetime.utcnow()
utc_then = utc_now - datetime.timedelta(days=1)

utc_month = datetime.date.strftime(utc_then, '%m')
utc_year = datetime.date.strftime(utc_then, '%Y')
utc_day = datetime.date.strftime(utc_then, '%d')
# utc_day = "13"

utc_reverse_date = utc_then.strftime('%Y-%m-%d')
utc_hour = utc_then.strftime('%H')

# heado = [str(x).strip() for x in range(0,50)]
# heado.insert(0, "What")
# heado.append("UTC Date")

# %%

wiki_linko = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia.org/all-access/{utc_year}/{utc_month}/{utc_day}"
# https://pageviews.wmcloud.org/topviews/?project=en.wikipedia.org&platform=all-access&date=last-month&excludes=#
# https://pageviews.wmcloud.org/topviews/?project=en.wikipedia.org&platform=all-access&date=last-month&excludes=#
# https://pageviews.wmcloud.org/topviews/?project=en.wikipedia.org&platform=all-access&date=yesterday&excludes=#

# https://pageviews.wmcloud.org/topviews/?project=en.wikipedia.org&platform=all-access&date=2015-07-01&excludes=#
# https://pageviews.wmcloud.org/topviews/?project=en.wikipedia.org&platform=all-access&date=yesterday&excludes=#

# wiki_linko = f"https://pageviews.wmcloud.org/topviews/?project=en.wikipedia.org&platform=all-access&date={utc_year}-{utc_month}-{utc_day}&excludes=#"

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
'Accept-Language': "en-GB,en-US;q=0.9,en;q=0.8",
"Referer": 'https://www.google.com',
"DNT":'1'}

wiki_r = requests.get(wiki_linko, headers=headers)

# print(wiki_r.status_code)
# print(wiki_r.url)
# %%

# print(wiki_r.text)

# %%



# %%

if wiki_r.status_code != 404:

    # print(wiki_r.url)

    # print(wiki_r.text)

    wiki_trends = json.loads(wiki_r.text)
    wiki_trends = wiki_trends['items'][0]['articles']
    # wiki_trends = wiki_trends[2:52]

    # wiki_trends = [x['article'] for x in wiki_trends]



    df = pd.DataFrame(wiki_trends)
    df = df.rename(columns={"article": "Page", "views": "Views", 'rank': "Rank"})
    # df['Page'] = df['Page'].str.replace("_", " ")

    # %%

    zdf = df.copy()
    zdf = zdf[['Rank', 'Page', 'Views']]

    # %%


    

    send_to_s3(scrape_time, 'wiki', zdf)

    send_to_git(scrape_date_stemmo, 'Archives', 'wiki', zdf)

