
# %%

import requests
import os 
import shutil
import pandas as pd 
import boto3
import dateparser 
import re
import json 
import pytz
import datetime 

import pathlib
pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

from dotenv import load_dotenv
load_dotenv()

AWS_KEY = os.environ['awsykey']
AWS_SECRET = os.environ['awsysec']

# %%

session = boto3.Session(
        aws_access_key_id=AWS_KEY,
        aws_secret_access_key=AWS_SECRET,
        )

s3 = session.resource('s3')

s3_client = session.client('s3')

# %%

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

pathos = '/Users/josh/Github/oz_weather_scraper/data/raw/'

dirt = os.listdir(pathos)
dirt = [x for x in dirt if os.path.isdir(f"{pathos}{x}")]
# dirt = [pathos + x for x in dirt if os.path.isdir(f"{pathos}{x}")]
# dirt = [x for x in dirt if x == 'wiki']

cities = ['Sydney', 'Adelaide', 'Melbourne', 'Canberra', 'Brisbane', 'Hobart', 'Perth', 'Darwin']

# %%
lenno = len(dirt)
counter = 1
for fold in dirt:
    print(f"{counter}/{lenno}")
    counter += 1

    fold_datto = dateparser.parse(fold, date_formats=['%Y%m%d'])
    fold_datto_format = fold_datto.strftime("%Y_%m_%d")

    iterrer = pathlib.Path(f"{pathos}{fold}")
    fillos = list(iterrer.rglob("*.csv"))

    fillos = [str(x) for x in fillos]

    for city in cities:
        inter_fillos = [x for x in fillos if city.lower() in x.lower()]

        listo = []
        if len(inter_fillos) > 0:
            for thingo in inter_fillos:
                scrape_stemmo = thingo.split("/")[-1].split('_')[1]
                scrape_datto_format = f"{fold_datto_format}_{scrape_stemmo}"

                inter = pd.read_csv(thingo)
                inter['Scraped'] = scrape_datto_format

                listo.append(inter)
            cat = pd.concat(listo)

            for timmo in cat['Scraped'].unique().tolist():

                scrape_time = dateparser.parse(timmo, date_formats=['%Y_%m_%d_%H'], settings={'TIMEZONE': "Australia/Brisbane"})
                
                fin = cat.loc[cat['Scraped'] == timmo].copy()
                fin.fillna('', inplace=True)

                send_to_s3(scrape_time, "oz-weather", fin,agent=city)

