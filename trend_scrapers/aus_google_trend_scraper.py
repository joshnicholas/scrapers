# %%
import pandas as pd
from pytrends.request import TrendReq
import datetime
import pytz

import pathlib
import os 
pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

# %%

def dumper(path, name, frame):
    with open(f'{path}/{name}.csv', 'w') as f:
        frame.to_csv(f, index=False, header=True)

utc_now = pytz.utc.localize(datetime.datetime.utcnow())
brissie = utc_now.astimezone(pytz.timezone("Australia/Brisbane"))
bris_reverse_date = brissie.strftime('%Y-%m-%d')
bris_hour = brissie.strftime('%H')

today = datetime.datetime.now()
scrape_date_stemmo = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y%m%d')
scrape_hour = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%H')

# %%

pytrend = TrendReq(hl='en-US', tz=360)

df = pytrend.trending_searches(pn='australia')
df.rename(columns={0: "Search"}, inplace=True)

# %%

zdf = df.copy()
zdf['Rank'] = zdf.index + 1

zdf = zdf[['Rank', 'Search']]

print(zdf)

dumper('../archive/google', 'latest', zdf)

dumper('../archive/google/daily_dumps', scrape_date_stemmo, zdf)

with open(f'../static/latest_google.json', 'w') as f:
    zdf.to_json(f, orient='records')





# %%
