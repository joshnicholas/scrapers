# %%
import requests
import pandas as pd 
from bs4 import BeautifulSoup as bs 
import pytz
import datetime
import json

import sys

import pathlib
import os 
pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

# from selenium import webdriver 
# from selenium.webdriver.chrome.options import Options

# chrome_options = Options()
# chrome_options.add_argument("--headless")
# # chrome_options.add_argument('--no-sandbox') 
# driver = webdriver.Chrome(options=chrome_options)

import time
from github import Github, UnknownObjectException

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


r = requests.get("https://www.sbs.com.au/news/collection/top-stories", headers=headers)


# start_url = "https://www.sbs.com.au/news/collection/top-stories"
# driver.get(start_url)



# %%


soup = bs(r.text, 'html.parser')
div = soup.find("div", {"data-layer-event-source-title":"Top Stories"})


items = div.find_all("a", {"data-testid":"internal-link"})
items = [x for x in items if x.find('h2')]

# print(items[:2])
counter = 1

sent = 0

records = []

for thing in items:

    try:

        heado = thing.h2.text

        # print(heado)

        linko = thing['href']
        linko = 'https://www.sbs.com.au' + linko
        # print(linko)

        dicto = {"publication": "SBS",

        'scraped_datetime': format_scrape_time,
        'Headline': heado.replace("analysis:", '').strip(),
        'Url': linko.strip(),
        'Rank': counter
        }

        counter += 1

        records.append(dicto)

    except Exception as e:

        print(f"Exception is {e}")
        print(f"Line: {sys.exc_info()[-1].tb_lineno}")
        continue




df = pd.DataFrame.from_records(records)

def create_search(what, frame):
    import nltk
    from nltk.stem import WordNetLemmatizer
    nltk.download("wordnet")
    nltk.download("omw-1.4")
    import re 

    def do_it(texto):

        wnl = WordNetLemmatizer() 

        senno = ''

        inside_texto = re.sub(r'[^A-Za-z0-9 ]+', '', texto)
        for word in inside_texto.split(" "):
            senno += f"{word.lower()} "

            stemmed = wnl.lemmatize(word)

            if stemmed.lower() not in senno:
                senno += f"{stemmed} "

        return senno

    copier = frame.copy()
    copier.fillna('', inplace=True)
    copier['Search_var'] = copier[what].map(lambda x: do_it(x))

    return copier


df = create_search("Headline", df)

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

    

send_to_s3(scrape_time, 'sbs_top', df)

send_to_git(format_scrape_time, 'Archives', 'sbs_top', df)

# %%
