# %%
import pandas as pd 
import os 
import pathlib
import time

import datetime
import pytz

from selenium import webdriver 
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

chrome_options = Options()
# chrome_options.add_argument("--headless")
driver = webdriver.Firefox(options=chrome_options)

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

    fillos = os.listdir(pathos)
    print(fillos)

    if f'{nammo}.csv' not in fillos:
        print("if")
        dumper(pathos, nammo, new)
    
    else:
        print("else")
        old = pd.read_csv(f"{pathos}{nammo}.csv")

        tog = pd.concat([new, old])
        tog.drop_duplicates(subset=[drop_col], inplace=True)
        tog.sort_values(by=[sort_col], ascending=False, inplace=True)
        dumper(pathos, nammo, tog)


# %%

today = datetime.datetime.now()
scrape_date_stemmo = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y%m%d')
scrape_hour = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%H')

# %%

pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

#%%


urlo = f'https://www.homeaffairs.gov.au/access-and-accountability/freedom-of-information/disclosure-logs/{this_year}'

driver.get(urlo)
# /html/body/form/div[3]/div[2]/div[2]/div[3]/main/div/div[5]/div[2]/div/div[2]/div[2]/div/div[1]/div/div/div/div[1]/ha-table-search/div/div[2]/div/ha-paginator/nav/ul/li[11]/a
# /html/body/form/div[3]/div[2]/div[2]/div[3]/main/div/div[5]/div[2]/div/div[2]/div[2]/div/div[1]/div/div/div/div[1]/ha-table-search/div/div[2]/div/ha-paginator/nav/ul/li[10]/a
#table-search > div.content.bg-white > div > ha-paginator > nav > ul > li:nth-child(10) > a

<a href="#">
          Next
        </a>

while True:

    try:

        # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="table-search"]/div[2]/div/ha-paginator/nav/ul/li[10]/a'))).click()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, 'Next'))).click()

        rand_delay(2)

    except Exception as e:
        print(e)


    else:
        print("No more pages left")
        break


    finally:
        time.sleep(5)
        driver.quit()