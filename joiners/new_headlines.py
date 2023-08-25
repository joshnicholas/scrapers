# %%
# import requests
import pandas as pd 
from sentence_transformers import SentenceTransformer, util
import time 
import pathlib
import os 
from github import Github, UnknownObjectException
import json
import math 
pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

from dotenv import load_dotenv
load_dotenv()

from newsplease import NewsPlease
import requests

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
'Accept-Language': "en-GB,en-US;q=0.9,en;q=0.8",
"Referer": 'https://www.google.com',
"DNT":'1'}



# %%
import pytz
import datetime
today = datetime.datetime.now()

scrape_date_stemmo = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y%m%d')
scrape_time = today.astimezone(pytz.timezone("Australia/Brisbane"))

format_scrape_time = datetime.datetime.strftime(scrape_time, "%Y_%m_%d_%H")

# %%

to_check = ['abc_top', 'graun_top', 'sbs_top', 'smh_top']

def get_latest_s3(checkers, scrape_time, extra = False):
    import boto3

    yesterday = scrape_time - datetime.timedelta(days=1)
    month_ago = scrape_time.replace(day=1) - datetime.timedelta(days=1)
    twelve_ago = scrape_time - datetime.timedelta(hours=12)

    format_scrape_month = datetime.datetime.strftime(scrape_time, "%Y_%m")
    format_scrape_last_month = datetime.datetime.strftime(month_ago, "%Y_%m")

    format_scrape_day = datetime.datetime.strftime(scrape_time, "%Y_%m_%d")
    format_scrape_yesterday = datetime.datetime.strftime(yesterday, "%Y_%m_%d")
    
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

    listo = []
    for what in checkers:
        response = s3_client.get_object(Bucket='chaluchasu', Key=f"{what}/latest.json")
        inter = pd.read_json(response.get("Body"))
        listo.append(inter)
        time.sleep(2)

    cat = pd.concat(listo)
    return cat



testo = get_latest_s3(to_check, scrape_time)

# %%

records = []

urls = testo['Url'].unique().tolist()

def convertToNumber(s):
    return int.from_bytes(s.encode()[-20:], 'little')

def convertFromNumber (n):
    en = int(n)
    return en.to_bytes(math.ceil(n.bit_length() / 8), 'little').decode()


for urlo in urls:
    print(urlo)
    eyedee = convertToNumber(urlo)
    already_done = os.listdir('../Text_archive')

    if f"{eyedee}.txt" not in already_done:
        r = requests.get(urlo, headers=headers)
        texto = r.text
        print(r.status_code)
        with open(f"../Text_archive/{eyedee}.txt", 'w') as f:
            f.write(texto)
        time.sleep(2)
    else:
        print("Skipped")
        with open(f"../Text_archive/{eyedee}.txt",'r') as file:
            texto = file.read()

    article = NewsPlease.from_html(texto, url=None)
    record = {"Url": urlo, 'Text': article.maintext}
    records.append(record)




texts = pd.DataFrame.from_records(records)

# %%

texts = texts.loc[texts['Text'] != None]
texts.dropna(subset=['Text'], inplace=True)
print(texts)

# %%


embedder = SentenceTransformer('all-MiniLM-L6-v2')

corpus = texts['Text'].unique().tolist()

corpus_embeddings = embedder.encode(corpus, convert_to_tensor=True)

records = []

# Find the closest sentences of the corpus for each in corpus based on cosine similarity
top_k = min(5, len(corpus))
for query in corpus:

    group = []
    query_embedding = embedder.encode(query, convert_to_tensor=True)

    # Alternatively, we can also use util.semantic_search to perform cosine similarty + topk
    hits = util.semantic_search(query_embedding, corpus_embeddings, top_k=5)
    hits = hits[0]      #Get the hits for the first query
    # print(hits)
    for hit in hits:
        if hit['score'] > 0.8:
            group.append(hit['corpus_id'])
            # print(corpus[hit['corpus_id']], "(Score: {:.4f})".format(hit['score']))

    lenno = len(group)
    group.sort(reverse=True)
    group = [str(x) for x in group]
    group = ",".join(group)

    record = {"Text": query, "Matches": group, "Num matches": lenno}
    records.append(record)

# %%

grouped = pd.DataFrame.from_records(records)

### Link back to urls to use as key

linked = pd.merge(texts, grouped, on='Text', how='left')
linked.sort_values(by=['Num matches','Matches'], ascending=False, inplace=True)


tog = pd.merge(testo,linked, on='Url', how='left')
tog.sort_values(by=['Num matches', 'Matches'], ascending=False, inplace=True)

tog.dropna(subset=['Text'], inplace=True)

# print(tog)
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


zog = tog.copy()

zog['scraped_datetime'] = pd.to_datetime(zog['scraped_datetime'], format="%Y%m%d%M")

zog['scraped_datetime'] = zog['scraped_datetime'].dt.strftime("%M%p %d/%m%/%y")



# %%

bog = zog.copy()
bog.loc[bog['Matches'] == bog.index.astype(str), 'Matches'] = '-1'

# bog = bog[['Headline', 'publication', 'Matches']]
# print(bog)
# zog.loc[zog['Matches'] == str(zog.index), 'Matches'] = '-1'

print(tog.columns.tolist())

print(zog[['Headline', "Text"]])

from sudulunu.helpers import dumper
dumper('../inter', 'testo', zog)

# %%


# send_to_git(format_scrape_time, 'Archives', 'headlines', zog)




# %%
