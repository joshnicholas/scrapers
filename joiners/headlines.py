# %%
# import requests
import pandas as pd 
from sentence_transformers import SentenceTransformer, util
import time 
import pathlib
import os 
import json
pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

from github import Github, UnknownObjectException

from dotenv import load_dotenv
load_dotenv()

# %%
import pytz
import datetime
today = datetime.datetime.now()

scrape_date_stemmo = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y%m%d')
scrape_time = today.astimezone(pytz.timezone("Australia/Brisbane"))

format_scrape_time = datetime.datetime.strftime(scrape_time, "%Y_%m_%d_%H")

# %%

def get_latest(repo, checkers, scrape_time):


    yesterday = scrape_time - datetime.timedelta(days=1)
    twelve_ago = scrape_time - datetime.timedelta(hours=12)
    format_scrape_day = datetime.datetime.strftime(scrape_time, "%Y_%m_%d")
    format_scrape_yesterday = datetime.datetime.strftime(yesterday, "%Y_%m_%d")
    format_scrape_12_ago = datetime.datetime.strftime(twelve_ago, "%Y_%m_%d_%H")

    print(format_scrape_day)
    print(format_scrape_yesterday)

    tokeny = os.environ['gitty']
    github = Github(tokeny)

    repository = github.get_user().get_repo('Archives')

    for pathos in checkers:
        # print(pathos)
        # contents = repository.get_contents(f"{repo}/{pathos}/daily_dumps")

        totes = github.get_user().get_repo(f"{repo}/{pathos}/daily_dumps").totalCount
        print("Totes: ", totes)

        contents = repository.get_contents(f"{repo}/{pathos}/daily_dumps")

        # ### I think I need to access the contents recursively?
        # while contents:
        #     file_content = contents.pop(0)
        #     if file_content.type == "dir":
        #         contents.extend(repo.get_contents(file_content.path))
        #     else:
        #         print(file_content)

        print(len(contents))

        fillos = [x.path.replace(f"{pathos}/", '') for x in contents]
        # fillos = [x for x in fillos if any(s in x for s in ["2023_08"])]

        # fillos = [x for x in fillos if any(s in x for s in [format_scrape_day, format_scrape_yesterday])]

        # print(pathos)
        # print("contents: ", contents)
        # print("fillos: ", fillos)
    return fillos

### Check github directories for the latest 
to_check = ['abc_top', 'graun_top', 'sbs_top']

# get_latest('Archive', ['graun_top'], scrape_time)

# %%

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

        there = []
        for datto in [format_scrape_month, format_scrape_last_month]:
            if extra:
                new_path = f"{what}/{extra}/{datto}/"
            else:
                new_path = f"{what}/dumps/{datto}/"

            # print(new_path)
            response = s3_client.list_objects_v2(Bucket='chaluchasu', Prefix=new_path)
            # print(response)
            inter = [x['Key'] for x in response['Contents']]
            # print(inter)
            inter = [x for x in inter if any(s in x for s in [format_scrape_day, format_scrape_yesterday])]

            there.extend(inter)
        
        for thing in there:
            response = s3_client.get_object(Bucket='chaluchasu', Key=thing)
            inter = pd.read_json(response.get("Body"))
            # print(inter)
            listo.append(inter)
        time.sleep(2)

    cat = pd.concat(listo)
    return cat



testo = get_latest_s3(to_check, scrape_time)




# %%

print(testo)

print(testo.columns.tolist())

# %%


# urls = ["https://raw.githubusercontent.com/joshnicholas/Archives/main/Archive/abc_top/latest.json",
# "https://raw.githubusercontent.com/joshnicholas/Archives/main/Archive/graun_top/latest.json",
# "https://raw.githubusercontent.com/joshnicholas/Archives/main/Archive/sbs_top/latest.json"]


# listo = []

# for urlo in urls:
#     inter = pd.read_json(urlo)
#     listo.append(inter)
#     # print(inter)
#     # print(inter.columns.tolist())
#     # 'publication', 'scraped_datetime', 'Headline', 'Url', 'Rank'

# # %%

# cat = pd.concat(listo)
# cat = cat[['publication', 'scraped_datetime', 'Headline', 'Url', 'Rank']]
# print(cat)

cat = testo.copy()

# https://www.sbert.net/examples/applications/semantic-search/README.html


embedder = SentenceTransformer('all-MiniLM-L6-v2')

corpus = cat['Headline'].unique().tolist()

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
        if hit['score'] > 0.5:
            group.append(hit['corpus_id'])
            # print(corpus[hit['corpus_id']], "(Score: {:.4f})".format(hit['score']))

    lenno = len(group)
    group.sort(reverse=True)
    group = [str(x) for x in group]
    group = ",".join(group)

    record = {"Headline": query, "Matches": group, "Num matches": lenno}
    records.append(record)

test = pd.DataFrame.from_records(records)
test.sort_values(by=[ 'Matches', 'Num matches'], ascending=False, inplace=True)


tog = pd.merge(cat, test, on='Headline', how='left')
tog.sort_values(by=['Num matches', 'Matches'], ascending=False, inplace=True)

# %%

zog = tog.copy()

zog['scraped_datetime'] = pd.to_datetime(zog['scraped_datetime'], format="%Y%m%d%M")

zog['scraped_datetime'] = zog['scraped_datetime'].dt.strftime("%M%p %d/%m%/%y")

print(zog)
# %%


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


def send_to_s3(scrape_time, what, frame):
    import boto3
    yesterday = scrape_time - datetime.timedelta(days=1)
    twelve_ago = scrape_time - datetime.timedelta(hours=12)
    format_scrape_day = datetime.datetime.strftime(scrape_time, "%Y_%m_%d")
    format_scrape_yesterday = datetime.datetime.strftime(yesterday, "%Y_%m_%d")
    format_scrape_month = datetime.datetime.strftime(scrape_time, "%Y_%m")
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

    copier = frame.copy()
    copier.fillna('', inplace=True)

    jsony = copier.to_dict(orient='records')
    content = json.dumps(jsony)

    latest_path = f"{what}/latest.json"
    archive_path = f"{what}/dumps/{format_scrape_month}/{format_scrape_time}.json"

    print(archive_path)

    s3_client.put_object(
     Body=content,
     Bucket='chaluchasu',
     Key=latest_path
    )

    s3_client.put_object(
     Body=content,
     Bucket='chaluchasu',
     Key=archive_path
    )

    

send_to_s3(scrape_time, 'headlines', zog)

send_to_git(format_scrape_time, 'Archives', 'headlines', zog)