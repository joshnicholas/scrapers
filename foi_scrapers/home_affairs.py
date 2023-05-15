# %%
import pandas as pd 
import os 
import pathlib
import time 

import sys 

pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

# print("cwd:", os.getcwd())

import datetime
import pytz

from selenium import webdriver 
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

from bs4 import BeautifulSoup as bs 

# %%
### Get the current year

this_year = datetime.datetime.now().strftime("%Y")

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

agency = 'home_affairs'

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

today = datetime.datetime.now()
scrape_date_stemmo = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y%m%d')
scrape_hour = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%H')



#%%

# print('this_year: ', this_year)

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
'Accept-Language': "en-GB,en-US;q=0.9,en;q=0.8",
"Referer": 'https://www.google.com',
"DNT":'1'}

urlo = f'https://www.homeaffairs.gov.au/access-and-accountability/freedom-of-information/disclosure-logs/{this_year}'
home = urlo 
driver.get(urlo)

time.sleep(5)

soup = bs(driver.page_source, 'html.parser')

box = soup.find(class_="content")

print(urlo)

# %%

cards = box.find_all("tr", attrs={"tabindex": -1})
# print("lenno: ", len(cards))
# print(cards)

# %%


listo = []

for card in cards:
    try:
        # print(card)

        teeds = card.find_all('td')
        
        datto = teeds[0].text
        datto = datetime.datetime.strptime(datto, "%d/%m/%Y")
        datto = datto.strftime("%Y-%m-%d")
        # print(datto)

        stemmo = teeds[1].text
        # print(stemmo)

        pees = teeds[2].find_all('p')
        
        # for pee in teeds[2].find_all('p'):
        #     print(pee)

        title = pees[0].text
        # print(title)

        # print(pees)
        file_path = pees[1].a['href']
        # print(urlo)

        file = 'https://www.homeaffairs.gov.au' + file_path
        # print(file)

        record = {"Agency": "Home Affairs",
                  "Date": datto,
                  "Id": stemmo,
                  "Title": title,
                  "Url": urlo,
                "Home_url": home,
                  "File": file}
        
        listo.append(record)


    except Exception as e:

        print(urlo)
        print(f"Exception is {e}")
        print(f"Line: {sys.exc_info()[-1].tb_lineno}")
        continue


cat = pd.DataFrame.from_records(listo)

send_foi_to_git(f"{format_scrape_time}_{agency}", 'Archives', 'foi', agency, cat)