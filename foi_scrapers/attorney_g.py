# %%
import pandas as pd 
import dateparser

import requests
from bs4 import BeautifulSoup as bs

import datetime 
import pytz
import sys
import re

import os 
import pathlib

today = datetime.datetime.now()
scrape_date_stemmo = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y%m%d')
scrape_time = today.astimezone(pytz.timezone("Australia/Brisbane"))
format_scrape_time = datetime.datetime.strftime(scrape_time, "%Y_%m_%d_%H")

import json 
import time
from github import Github, UnknownObjectException

from dotenv import load_dotenv
load_dotenv()

# %%

agency = 'attorney_general'

def send_foi_to_git(stemmo, repo, what, agent, frame):

    tokeny = os.environ['gitty']

    github = Github(tokeny)

    repository = github.get_user().get_repo(repo)

    jsony = frame.to_dict(orient='records')
    content = json.dumps(jsony)

    filename = f'Archive/{what}/daily_dumps/{stemmo}.json'

    inter = f'Archive/{what}/inter/{agent}.json'

    def check_do(pathos):
        contents = repository.get_contents(pathos)

        fillos = [x.path.replace(f"{pathos}/", '') for x in contents]

        # print(pathos)
        # print("contents: ", contents)
        # print("fillos: ", fillos)
        return fillos

    # donners = check_do(f'Archive/{what}/daily_dumps')

    def try_file(pathos):
        try:
            repository.get_contents(pathos)
            return True
        except UnknownObjectException as e:
            return False

    # latest_donners = check_do(f'Archive/{what}')
    # donners = check_do(f'Archive/{what}/daily_dumps')
    donners = try_file(filename)

    latters = repository.get_contents(inter)
    repository.update_file(inter, f"updated_scraped_file_{stemmo}", content, latters.sha)

    if donners == False:

        repository.create_file(filename, f"new_scraped_file_{stemmo}", content)



# %%

pathos = pathlib.Path(__file__).parent
os.chdir(pathos)


# %%

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
'Accept-Language': "en-GB,en-US;q=0.9,en;q=0.8",
"Referer": 'https://www.google.com',
"DNT":'1'}

urlo = 'https://www.ag.gov.au/rights-and-protections/freedom-information/freedom-information-disclosure-log'
home = urlo
r = requests.get(urlo, headers=headers)

soup = bs(r.text, 'html.parser')

# %%

body = soup.find('table')

rows = body.find_all('tr')

listo = []

for row in rows[1:10]:
    # print(row)
    try:
        cells = row.find_all('td')

        id = row.find('th').text.strip()
        # print(id)

        datter = cells[0].text.strip()
        # print(datter)
        parsed = dateparser.parse(datter)
        datto = parsed.strftime("%Y-%m-%d")
        # print(datto)

        texto = cells[1]

        # title = texto.find('p').text.strip()
        title = texto.text.strip()
        title = re.sub(r"\s+", ' ', title)

        # print(title)

        # # print(texto)
        
        # all_text = texto.text.strip()

        file_url = cells[2].text.strip()
        fillo = file_url

        record = {"Agency": agency,
                "Date": datto,
                "Id": id,
                "Title": title.encode().decode("utf-8"),
                # "Text": all_text, 
                "Url": urlo,
                "File": fillo}
        listo.append(record)


        # print(record)
        # print(id)
        # print(datto)
        # print(cells[0])
    except Exception as e:

        print(urlo)
        print(f"Exception is {e}")
        print(f"Line: {sys.exc_info()[-1].tb_lineno}")
        continue
# %%

cat = pd.DataFrame.from_records(listo)
# print(cat)


def send_foi_to_s3(scrape_time, what, agent, frame):
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

    latest_path = f"{what}/{agent}.json"
    archive_path = f"{what}/dumps/{agent}/{format_scrape_time}.json"

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

    

# print(cat)
send_foi_to_s3(scrape_time, 'foi', agency, cat)


send_foi_to_git(f"{format_scrape_time}_{agency}", 'Archives', 'foi', agency, cat)
# %%


