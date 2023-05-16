# %%
import requests
import json 

import pandas as pd 
import datetime 
import pytz
import os 

today = datetime.datetime.now()

scrape_date_stemmo = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y%m%d')

scrape_time = today.astimezone(pytz.timezone("Australia/Brisbane"))
format_scrape_time = datetime.datetime.strftime(scrape_time, "%Y_%m_%d_%H")

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
        


# %%

cookies = {
    'monsido': '9181678067854536',
    'WSS_FullScreenMode': 'false',
    '_ga_ZJCQF0YHGH': 'GS1.1.1678090110.2.0.1678090133.0.0.0',
    '_ga': 'GA1.1.1064361373.1678067857',
    '_ga': 'GA1.4.1064361373.1678067857',
    '_gid': 'GA1.4.1569187401.1678067858',
    'ln_or': 'eyIyODUxMDEwIjoiZCJ9',
    '_gid': 'GA1.3.1569187401.1678067858',
    '_dc_gtm_UA-61305954-17': '1',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/110.0',
    'Accept': 'application/json;odata=verbose',
    'Accept-Language': 'en-GB,en;q=0.5',
    # 'Accept-Encoding': 'gzip, deflate, br',
    # Already added when you pass json=
    # 'Content-Type': 'application/json',
    'X-RequestDigest': '0x4AD2B759CA5EE34AA7CCFF6210320CF2EE806F7BA0F35E50DD61BDEC6907F47041647EE445133B82E08C5FDBF55FFB04D357E164F0F6AA7AB5BD4FB8D9A1DD2D,06 Mar 2023 08:08:37 -0000',
    'Origin': 'https://immi.homeaffairs.gov.au',
    'Connection': 'keep-alive',
    'Referer': 'https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-processing-times/global-processing-times',
    # 'Cookie': 'monsido=9181678067854536; WSS_FullScreenMode=false; _ga_ZJCQF0YHGH=GS1.1.1678090110.2.0.1678090133.0.0.0; _ga=GA1.1.1064361373.1678067857; _ga=GA1.4.1064361373.1678067857; _gid=GA1.4.1569187401.1678067858; ln_or=eyIyODUxMDEwIjoiZCJ9; _gid=GA1.3.1569187401.1678067858; _dc_gtm_UA-61305954-17=1',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}

json_data = {}

response = requests.post(
    'https://immi.homeaffairs.gov.au/_layouts/15/api/GPT.aspx/GetVisaGPTList',
    cookies=cookies,
    headers=headers,
    json=json_data,
)

# %%

# print(response.text)


jsony = json.loads(response.text)

records = jsony['d']['data']

print(records)
# %%


data = pd.DataFrame.from_records(records)

# print(data)
# print(data.columns.tolist())
# %%


df = data[['visaSubclassCode', 'visaSubclassText', 'visaSubclassSort', 'visaCategory', 'streamCode', 'streamText', 'percent75', 'percent90', 'percent25', 'percent50', 'updated', 'endDate', 'additionalInfo']].copy()

send_to_git(format_scrape_time, 'Archives', 'aus_visa_wait', df)