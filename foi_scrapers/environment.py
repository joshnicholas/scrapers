# %%
import pandas as pd 

import requests
from bs4 import BeautifulSoup as bs

import datetime 
import pytz
import sys

import os 
import pathlib

today = datetime.datetime.now()
scrape_date_stemmo = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y%m%d')
scrape_time = today.astimezone(pytz.timezone("Australia/Brisbane"))
format_scrape_time = datetime.datetime.strftime(scrape_time, "%Y_%m_%d_%H")

import json 
import time
from github import Github

# %%

agency = 'environment'

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

        print(pathos)
        print("contents: ", contents)
        print("fillos: ", fillos)
        return fillos

    donners = check_do(f'Archive/{what}/daily_dumps')

    latters = repository.get_contents(inter)
    repository.update_file(inter, f"updated_scraped_file_{stemmo}", content, latters.sha)

    if f"{stemmo}.json" not in donners:

        repository.create_file(filename, f"new_scraped_file_{stemmo}", content)



# %%

pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

# print("cwd:", os.getcwd())

#%%

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
'Accept-Language': "en-GB,en-US;q=0.9,en;q=0.8",
"Referer": 'https://www.google.com',
"DNT":'1'}

urlo = 'https://www.dcceew.gov.au/about/reporting/freedom-of-information/disclosure-log'
home = urlo
r = requests.get(urlo, headers=headers)

soup = bs(r.text, 'html.parser')


# %%

rows = soup.find_all('tr')

# donners = already_done('../archive/foi', 'treasury')
# print("donners: ", donners)

listo = []

for row in rows[1:]:

    # print(row)

    try:

        stemmo = row.find(attrs={"headers":"view-field-reference-table-column"}).text.strip()
        # print(stemmo)

        # if stemmo not in donners:
        
        datto = row.find(class_='datetime').text.strip()
        datto = datetime.datetime.strptime(datto, "%d %B %Y")
        datto = datto.strftime("%Y-%m-%d")
        # print(datto)

        title = row.find(attrs={"headers":"view-field-summary-table-column"}).text.strip()
        # print(title)

        # urlo = row.find(attrs={"headers":"view-title-table-column"}).a['href']
        urlo = row.find(class_='file--application-pdf').a['href']
        # print(urlo)

        file = 'https://www.dcceew.gov.au/' + urlo
        # print(file)

        record = {"Agency": "Environment",
                "Date": datto,
                "Id": stemmo,
                "Title": title,
                "Url": urlo,
                "Home_url": home,
                "File": file}
        listo.append(record)


    except AttributeError as e:

        print(urlo)
        print(f"Exception is {e}")
        print(f"Line: {sys.exc_info()[-1].tb_lineno}")
        continue


cat = pd.DataFrame.from_records(listo)

send_foi_to_git(f"{format_scrape_time}_{agency}", 'Archives', 'foi', agency, cat)
    
    # print(record)
    # create_raw_append_csv('../archive/foi', 'environment', record, "Id", 'Date')

# print(rows[1])
# %%
# https://www.dcceew.gov.au/about/reporting/freedom-of-information/disclosure-log#:~:text=Environment%20and%20Water-,72528.pdf,-72894