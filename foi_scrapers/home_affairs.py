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


# %%

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

def create_raw_append_csv(pathos, nammo, new_record, drop_col, sort_col):

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
        tog.drop_duplicates(subset=[drop_col], inplace=True)
        tog.sort_values(by=[sort_col], ascending=False, inplace=True)
        dumper(pathos, nammo, tog)


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



# %%

cards = box.find_all("tr", attrs={"tabindex": -1})
# print("lenno: ", len(cards))
# print(cards)

# %%

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
        urlo = pees[1].a['href']
        # print(urlo)

        file = 'https://www.homeaffairs.gov.au' + urlo
        # print(file)

        record = {"Agency": "Home Affairs",
                  "Date": datto,
                  "Id": stemmo,
                  "Title": title,
                  "Url": urlo,
                "Home_url": home,
                  "File": file}
        
        create_raw_append_csv('../data/foi', 'home_affairs', record, "Id", 'Date')

    except Exception as e:
        print(f"Exception is {e}")
        print(f"Line: {sys.exc_info()[-1].tb_lineno}")
        continue


# %%
