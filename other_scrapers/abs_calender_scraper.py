# %%
import pandas as pd 
import requests
import os 
import pathlib
from bs4 import BeautifulSoup as bs 

import dateparser
import datetime
from dateutil.relativedelta import relativedelta
import pytz

from selenium import webdriver 
# from selenium.webdriver.chrome.options import Options

# chrome_options = Options()
# chrome_options.add_argument("--headless")
# driver = webdriver.Chrome(options=chrome_options)

from selenium.webdriver.chrome.service import Service
service = Service()
options = webdriver.ChromeOptions()
options.add_argument("--headless")

driver = webdriver.Chrome(service=service, options=options)

import json 
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

        # print(pathos)
        # print("contents: ", contents)
        # print("fillos: ", fillos)
        return fillos


    # latest_donners = check_do(f'Archive/{what}')
    donners = check_do(f'Archive/{what}/daily_dumps')

    latters = repository.get_contents(latest)
    repository.update_file(latest, f"updated_scraped_file_{stemmo}", content, latters.sha)

    if f"{stemmo}.json" not in donners:

        repository.create_file(filename, f"new_scraped_file_{stemmo}", content)
        


# %%

today = datetime.datetime.now()

scrape_date_stemmo = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y%m%d')

scrape_time = today.astimezone(pytz.timezone("Australia/Brisbane"))
format_scrape_time = datetime.datetime.strftime(scrape_time, "%Y_%m_%d_%H")

# %%
### Get this month and next month for the scraper

next_month = today + relativedelta(months=1)
next_month = next_month.strftime("%Y%m")

this_month = today.strftime("%Y%m")


# %%

# %%

pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

#%%

listo = []

for month in [this_month, next_month]:

    urlo = f'https://www.abs.gov.au/release-calendar/future-releases/{month}'

    home = urlo 
    driver.get(urlo)

    time.sleep(5)

    soup = bs(driver.page_source, 'html.parser')

    box = soup.find(class_="view-content")


    rows = box.find_all(class_='views-row')

    for row in rows:
        # print(row)

        init_date = row.find(class_='datetime').text.strip()

        parsed = dateparser.parse(init_date)
        # print(parsed)
        datto = parsed.strftime("%Y-%m-%d")
        # print(datto)


        title = row.find(class_='event-name').text.strip()
        # print(title)

        desc = row.find(class_='views-field-body').text.strip()
        # print(desc)

        ref = row.find(class_='reference-period-value').text.strip()
        # print(ref)

        try:
            urlo = 'https://www.abs.gov.au' + row.a['href']
        except:
            urlo = ''
        # print(urlo)

        record = {"Release": title,
                "Description": desc,
                "Date": datto,
                "Url": urlo,
                'scraped_datetime': format_scrape_time}
        
        listo.append(record)



cat = pd.DataFrame.from_records(listo)

# print(cat)

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

    

send_to_s3(scrape_time, 'abs', cat)

send_to_git(format_scrape_time, 'Archives', 'abs', cat)

# # %%

# %%

driver.quit()