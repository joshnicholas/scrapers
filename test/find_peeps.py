# %%
import requests
import pandas as pd 
from bs4 import BeautifulSoup as bs 
import pytz
import datetime
import json
import boto3

import pathlib
import os 
pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

import time
from github import Github, UnknownObjectException

from collections import Counter

from dotenv import load_dotenv
load_dotenv()

import spacy
nlp = spacy.load("en_core_web_lg")


# %%
### Get all the endings

today = datetime.datetime.now().astimezone(pytz.timezone("Australia/Brisbane"))
endings = [(today - datetime.timedelta(hours=i)).strftime("%Y_%m_%d_%H") for i in range(0, 12)]
endings.insert

# %%

# urlos = ['https://raw.githubusercontent.com/joshnicholas/Archives/main/Archive/google_top/latest.json',
# 'https://raw.githubusercontent.com/joshnicholas/Archives/main/Archive/abc_top/latest.json',
# 'https://raw.githubusercontent.com/joshnicholas/Archives/main/Archive/sbs_top/latest.json',
# 'https://raw.githubusercontent.com/joshnicholas/Archives/main/Archive/graun_top/latest.json',
# 'https://raw.githubusercontent.com/joshnicholas/Archives/main/Archive/tech_meme_top/latest.json']

urlos = ['https://raw.githubusercontent.com/joshnicholas/Archives/main/Archive/google_top/daily_dumps/',
'https://raw.githubusercontent.com/joshnicholas/Archives/main/Archive/abc_top/daily_dumps/',
'https://raw.githubusercontent.com/joshnicholas/Archives/main/Archive/sbs_top/daily_dumps/',
'https://raw.githubusercontent.com/joshnicholas/Archives/main/Archive/graun_top/daily_dumps/']

# urlos = ['https://raw.githubusercontent.com/joshnicholas/Archives/main/Archive/graun_top/daily_dumps/']

def extract_names(urlos, endings):
    ignore = ['Health.com', 'Sky News Australia', 'Guardian Australia', 'The Guardian Australia', 
              'espn australia', 'MS - MS Australia', 'ESPN Australia', 'nt news', 'kotaku australia', 
              'The West Australian', 'Courier Mail', 'MS Australia', 'Tech Wire Asia', 'ABC News (Australia)', 
              'health.com', 'Monash University', 'The Australian', 'mirage news', 'sky news australia', 
              'the west australian', 'Sydney Morning Herald', 'ABC News', 'ABC', 'Mirage News', 
              'the guardian australia', 'Australia', 'amp.abc.net.au', 'the australian financial review', 
              'wion', '9news', 'The Conversation', 'Yahoo Lifestyle', 'abc news (australia)', 
              'The Australian Financial Review', 'Broadsheet', 'broadsheet', 'the australian', 
              'herald sun', 'Yahoo Lifestyle Australia', 'Herald Sun', 'CarExpert.com.au', 
              'Wide World of Sports', 'the guardian', '9Honey', 'Fox Sports', 'fox sports', 
              'Yahoo News Australia', 'Kotaku Australia', 'Guardian', 'EurekAlert', 'Griffith News', 
              '9News', 'The Strategist', 'abc news', 'WION', 'news.com.au', 'The Guardian', 
              'Adelaide Advertiser', 'Yahoo Finance Australia', 'adelaide advertiser', 'NT News', 
              "Sydney Children's Hospitals Network", 'Sky News', 'carexpert.com.au', 'Drive', 
              'the conversation', 'monash university', 'AZoCleantech', 'yahoo finance australia', 'Financial Review']
    
    listo = []
    lemmas = []

    for urlo in urlos:
        for ending in endings:
            try:
                # print(f"{urlo}{ending}.json")
                df = pd.read_json(f"{urlo}{ending}.json")

                headlines = df['Headline'].unique().tolist()
                for heado in headlines:
                    # print(heado)
                    if "google_top" in urlo:
                        pubs = df["publication"].unique().tolist()
                        ignore += pubs
                        # print(list(set(ignore)))

                        endo = heado.split("-")[-1].strip()

                        for thingo in pubs:
                            heado = heado.replace(thingo, "").strip()

                        ignore.append(endo)
                        ignore.append(endo.lower())

                    doc = nlp(heado)
                    ends = [e.text for e in doc.ents if (e.label_ in ('GPE', 'ORG', 'PERSON')) and (e.text not in ignore)]
                    # print(ends)
                    listo += ends
                    lems = [e.text.replace("'s",'').strip() for e in doc.ents if (e.label_ in ('GPE', 'ORG', 'PERSON')) and (e.text not in ignore)]
                    lemmas += lems
            except Exception as e:
                print(f"{e}: ", f"{urlo}{ending}.json")
                # print(f"{urlo}{ending}.json")
                continue


    # most_common_numbers = Counter(lemmas).most_common(10)
    # print(most_common_numbers)
    return listo, lemmas


listo, lemmas = extract_names(urlos, endings)

# %%

# print(lemmas)

most_common_numbers = Counter(lemmas).most_common(10)
print(most_common_numbers)

# def matcher 

# %%


# %%