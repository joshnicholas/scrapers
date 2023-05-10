# %%
import pandas as pd
import requests
import datetime
import json
import requests

import pytz
import pathlib
import os 
pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

# %%

def dumper(path, name, frame):
    with open(f'{path}/{name}.csv', 'w') as f:
        frame.to_csv(f, index=False, header=True)

# %%



today = datetime.datetime.now()
scrape_date_stemmo = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y%m%d')
scrape_hour = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%H')

utc_now = datetime.datetime.utcnow()
utc_then = utc_now - datetime.timedelta(days=1)

utc_month = datetime.date.strftime(utc_then, '%m')
utc_year = datetime.date.strftime(utc_then, '%Y')
utc_day = datetime.date.strftime(utc_then, '%d')

utc_reverse_date = utc_then.strftime('%Y-%m-%d')
utc_hour = utc_then.strftime('%H')

# heado = [str(x).strip() for x in range(0,50)]
# heado.insert(0, "What")
# heado.append("UTC Date")

# %%

wiki_linko = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia.org/all-access/{utc_year}/{utc_month}/{utc_day}"

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
'Accept-Language': "en-GB,en-US;q=0.9,en;q=0.8",
"Referer": 'https://www.google.com',
"DNT":'1'}

wiki_r = requests.get(wiki_linko, headers=headers)

wiki_trends = json.loads(wiki_r.text)
wiki_trends = wiki_trends['items'][0]['articles']
wiki_trends = wiki_trends[2:52]
wiki_trends = [x['article'] for x in wiki_trends]

df = pd.DataFrame(wiki_trends)
df = df.rename(columns={0: "Page"})
df['Page'] = df['Page'].str.replace("_", " ")



# %%

zdf = df.copy()
zdf['Rank'] = zdf.index + 1

zdf = zdf[['Rank', 'Page']]

# print(zdf)

dumper('../archive/wiki', 'latest', zdf)

dumper('../archive/wiki/daily_dumps', scrape_date_stemmo, zdf)

with open(f'../static/latest_wiki.json', 'w') as f:
    zdf.to_json(f, orient='records')

# %%
