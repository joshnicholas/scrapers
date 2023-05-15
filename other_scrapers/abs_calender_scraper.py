# %%
import pandas as pd 
import requests
import os 
import pathlib
from bs4 import BeautifulSoup as bs 

import time 

import dateparser
import datetime
from dateutil.relativedelta import relativedelta
import pytz

from selenium import webdriver 
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

import json 
import time
from github import Github

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

        print(pathos)
        print("contents: ", contents)
        print("fillos: ", fillos)
        return fillos


    # latest_donners = check_do(f'Archive/{what}')
    donners = check_do(f'Archive/{what}/daily_dumps')

    latters = repository.get_contents(latest)
    repository.update_file(latest, f"updated_scraped_file_{stemmo}", content, latters.sha)

    if f"{stemmo}.json" not in donners:

        repository.create_file(filename, f"new_scraped_file_{stemmo}", content)
        


##
def dumper(path, name, frame):
    with open(f'{path}/{name}.csv', 'w') as f:
        frame.to_csv(f, index=False, header=True)

##
def rand_delay(num):
  import random 
  import time 
  rando = random.random() * num
  print(rando)
  time.sleep(rando)

##
def if_no_fold_create(pathos, to_check):
    if pathos[-1] != '/':
        pathos += '/'

    folds = os.listdir(pathos)

    if to_check not in folds:
        os.mkdir(f"{pathos}{to_check}")

def create_raw_append_csv(pathos, nammo, new_record, drop_cols, sort_col):

    new = pd.DataFrame.from_records([new_record])

    if pathos[-1] != '/':
        pathos += '/'
    # print("cwd:", os.getcwd())
    fillos = os.listdir(pathos)

    if f'{nammo}.csv' not in fillos:
        # print("if")
        dumper(pathos, nammo, new)
    
    else:
        # print("else")
        old = pd.read_csv(f"{pathos}{nammo}.csv")

        tog = pd.concat([new, old])
        tog.drop_duplicates(subset=drop_cols, inplace=True)
        tog.sort_values(by=[sort_col], ascending=False, inplace=True)
        dumper(pathos, nammo, tog)

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

    if month not in os.listdir('../archive/abs/daily_dumps'):

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

            create_raw_append_csv('../archive/abs/daily_dumps', month, record, ["Release", 'Date'], 'Date')            

# # print(rows)
# # %%

cat = pd.DataFrame.from_records(listo)

print(cat)

# with open(f'../archive/abs/latest.csv', 'w') as f:
#     cat.to_csv(f, index=False, header=True)

# with open(f'../static/latest_abs.json', 'w') as f:
#     cat.to_json(f, orient='records')

send_to_git(format_scrape_time, 'Archives', 'abs', cat)

# # %%

# %%
