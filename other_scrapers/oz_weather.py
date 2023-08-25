# %%
import pandas as pd 
import os 
import requests
import json
import boto3

import time 

import datetime
import pytz
from dotenv import load_dotenv
load_dotenv()

# %%

today = datetime.datetime.now()
scrape_time = today.astimezone(pytz.timezone("Australia/Brisbane"))
format_scrape_time = datetime.datetime.strftime(scrape_time, "%Y_%m_%d_%H")
scrape_date_stemmo = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y%m%d')
scrape_hour = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%H')

# %%


def rand_delay(num):
  import random 
  import time 
  rando = random.random() * num
#   print(rando)
  time.sleep(rando)

def send_to_s3(scrape_time, what, frame,agent=False):

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

    if agent:

        latest_path = f"{what}/{agent}.json"
        archive_path = f"{what}/dumps/{agent}/{format_scrape_time}.json"
    
    else:
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

def scraper(stem, out_path, combo_path, urlo):

    print("## Starting: ", stem)

    # rand_delay(10)

    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    'Accept-Language': "en-GB,en-US;q=0.9,en;q=0.8",
    "Referer": 'https://www.google.com',
    "DNT":'1'}

    r = requests.get(urlo, headers=headers)

    # print("R status: ", r.status_code)
    tabs = pd.read_html(r.text)[1:]

    time.sleep(2)

    day_counter = 0

    listo = []

    for i in range(0, len(tabs)):

        if  'Temp (°C)' in tabs[i].columns.tolist():

            tabbo = tabs[i]

            inter_date = today  - datetime.timedelta(days=day_counter)
            inter_date_format = inter_date.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y-%m-%d')

            tabbo['Date'] = inter_date_format
            listo.append(tabbo)  
            day_counter += 1

    cat = pd.concat(listo)
    cat['Scraped'] = format_scrape_time

    send_to_s3(scrape_time, "oz-weather", cat,agent=stem)


scraper("Sydney", 'data/raw','data',  'http://www.bom.gov.au/places/nsw/turramurra/observations/sydney---observatory-hill/')

scraper("Melbourne", 'data/raw','data',  'http://www.bom.gov.au/places/vic/melbourne/observations/melbourne-(olympic-park)/')

scraper("Brisbane", 'data/raw','data',  'http://www.bom.gov.au/places/qld/brisbane/observations/brisbane/')

scraper("Perth", 'data/raw','data',  'http://www.bom.gov.au/places/wa/perth/observations/perth/')

scraper("Adelaide", 'data/raw','data',  'http://www.bom.gov.au/places/sa/adelaide/observations/adelaide-(west-terrace----ngayirdapira)/')

scraper("Hobart", 'data/raw','data',  'http://www.bom.gov.au/places/tas/hobart/observations/hobart/')

scraper("Canberra", 'data/raw','data',  'http://www.bom.gov.au/places/act/canberra/observations/canberra/')

scraper("Darwin", 'data/raw','data',  'http://www.bom.gov.au/places/nt/darwin/observations/darwin-harbour/')

# %%
