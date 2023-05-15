#%%

import requests

import datetime 
import pytz

import json
import pandas as pd

import os 
import pathlib
pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

utc_now = pytz.utc.localize(datetime.datetime.utcnow())
today = utc_now.astimezone(pytz.timezone("Asia/Colombo"))


today = datetime.datetime.now()

scrape_date_stemmo = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y%m%d')

scrape_time = today.astimezone(pytz.timezone("Australia/Brisbane"))
format_scrape_time = datetime.datetime.strftime(scrape_time, "%Y_%m_%d_%H")

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
        


cookies = {
    # 'AWSALB': 'VYHV7fnR3Hkt1wnhVCNDRHq7on7JvsSpPwkO2GYFwQE3JAOp0u1l+31JP1cFQSCYITavRpyLX7WVFhzJi2w6xdQqMi2tEwPR/hGbN6rhLiXw73QZzuSrpJimwKQg',
    # 'AWSALBCORS': 'VYHV7fnR3Hkt1wnhVCNDRHq7on7JvsSpPwkO2GYFwQE3JAOp0u1l+31JP1cFQSCYITavRpyLX7WVFhzJi2w6xdQqMi2tEwPR/hGbN6rhLiXw73QZzuSrpJimwKQg',
    # '_ga': 'GA1.2.618747044.1678063884',
    # '_fbp': 'fb.1.1678063886300.1902614845',
    # '_gid': 'GA1.2.23049639.1678418700',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/110.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/json',
    'Referer': 'https://www.cse.lk/pages/trade-summary/trade-summary.component.html',
    'Origin': 'https://www.cse.lk',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Connection': 'keep-alive',
    # 'Cookie': 'AWSALB=VYHV7fnR3Hkt1wnhVCNDRHq7on7JvsSpPwkO2GYFwQE3JAOp0u1l+31JP1cFQSCYITavRpyLX7WVFhzJi2w6xdQqMi2tEwPR/hGbN6rhLiXw73QZzuSrpJimwKQg; AWSALBCORS=VYHV7fnR3Hkt1wnhVCNDRHq7on7JvsSpPwkO2GYFwQE3JAOp0u1l+31JP1cFQSCYITavRpyLX7WVFhzJi2w6xdQqMi2tEwPR/hGbN6rhLiXw73QZzuSrpJimwKQg; _ga=GA1.2.618747044.1678063884; _fbp=fb.1.1678063886300.1902614845; _gid=GA1.2.23049639.1678418700',
    # Requests doesn't support trailers
    # 'TE': 'trailers',
}

json_data = {
    'headers': {
        'normalizedNames': {},
        'lazyUpdate': None,
    },
}

r = requests.post('https://www.cse.lk/api/tradeSummary', cookies=cookies, headers=headers, json=json_data)


jsony = json.loads(r.text)

listo = jsony['reqTradeSummery']

# print(listo)

if len(listo) > 1:
    df = pd.DataFrame.from_records(listo)

    df['scraped_datetime'] = format_scrape_time
    df['Date'] = scrape_date_stemmo

    # with open(f'../archive/cse/daily_dumps/{today_stem}.csv', 'w') as f:
    #     df.to_csv(f, index=False, header=True)

    # with open(f'../archive/cse/latest.csv', 'w') as f:
    #     df.to_csv(f, index=False, header=True)

    # with open('../static/cse.json', 'w') as f:
    #     df.to_json(f, orient='records')


    send_to_git(format_scrape_time, 'Archives', 'cse', df)
