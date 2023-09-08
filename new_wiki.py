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

if wiki_r.status_code != 404:

    # print(wiki_r.url)

    # print(wiki_r.text)

    wiki_trends = json.loads(wiki_r.text)
    wiki_trends = wiki_trends['items'][0]['articles']

    wiki_trends = [x['article'] for x in wiki_trends]

    df = pd.DataFrame(wiki_trends)
    df = df.rename(columns={0: "Page"})
    df['Page'] = df['Page'].str.replace("_", " ")

    print(df)


# %%

zdf = df.copy()
zdf['Rank'] = zdf.index + 1

zdf = zdf[['Rank', 'Page']]

print(df)
# %%
