# %%
import requests
import pandas as pd 
from bs4 import BeautifulSoup as bs 
import pytz
import datetime
import json
import boto3
import re
import pathlib
import os 
pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

import time
from github import Github, UnknownObjectException

from dotenv import load_dotenv
load_dotenv()

# %%

today = datetime.datetime.now()

scrape_date_stemmo = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y%m%d')

scrape_time = today.astimezone(pytz.timezone("Australia/Brisbane"))
format_scrape_time = datetime.datetime.strftime(scrape_time, "%Y_%m_%d_%H")

# %%

goog = pd.read_json('https://raw.githubusercontent.com/joshnicholas/Archives/main/Archive/google_top/latest.json')

listo = [goog]

urls = ['https://raw.githubusercontent.com/joshnicholas/Archives/main/Archive/abc_top/latest.json',
        'https://raw.githubusercontent.com/joshnicholas/Archives/main/Archive/graun_top/latest.json',
        'https://raw.githubusercontent.com/joshnicholas/Archives/main/Archive/sbs_top/latest.json']

for url in urls:
    inter = pd.read_json(url)
    listo.append(inter)

# %%


new_stops = goog['Headline'].unique().tolist()

goog_stems = [x.split('-')[-1].strip() for x in new_stops]

new_stops.extend(['from', 'subject', 're', 'edu', 'use',
                  'news', 'abc', 'guardian', 'australia', 
                  'australian', 'herald', 'aussie','9News',
                  '9News', 'news.com.au', '7NEWS', 'live', 'abc',
                  'ABC News', 'Reuters','Morning Herald',
                  'The West Australian','KitGuruTech', 'Engadget',
                  'Forbes', 'Yahoo','Mirage News', 'Medical.Net', 'Telegraph',
                  'Daily'])

new_stops = [x.split('-')[-1].strip() for x in new_stops]

new_stops = [re.split('\.|;|,| ', x) for x in new_stops]
new_stops = list(set([item.lower() for sublist in new_stops for item in sublist]))

# print(new_stops)

# %%

# %%

data = pd.concat(listo)

['publication', 'scraped_datetime', 'Headline', 'Url', 'Rank', 'Search_var', 'Publish datetime']

data['scraped_datetime'] = pd.to_datetime(data['scraped_datetime'], format="%Y%m%d%H")

latest = data['scraped_datetime'].max()

# print(len(data))
### Doing this to make sure we don't get old data if something errors

data = data.loc[data['scraped_datetime'] == latest]
# print(len(data))
# %%

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import ngrams
from collections import Counter
import nltk
# nltk.download('stopwords')


stop_words = stopwords.words('english')
stop_words.extend(new_stops)

# print(stop_words)

def word_frequency(sentences):

    sentence = " ".join(sentences)

    new_tokens = word_tokenize(sentence)

    new_tokens = [t.lower() for t in new_tokens]
    new_tokens =[t for t in new_tokens if t.lower() not in stop_words]
    new_tokens = [t for t in new_tokens if t.isalpha()]

    lemmatizer = WordNetLemmatizer()
    new_tokens =[lemmatizer.lemmatize(t) for t in new_tokens]

    counted = Counter(new_tokens)

    word_freq = pd.DataFrame(counted.items(),columns=['word','frequency']).sort_values(by='frequency',ascending=False)

    return word_freq

# data2 = word_frequency(data['Headline'].tolist())

# import seaborn as sns
# import matplotlib.pyplot as plt

# # create subplot of the different data frames
# fig, axes = plt.subplots(figsize=(8,20))

# sns.barplot(ax=axes,x='frequency',y='word',data=data2.head(60))
# plt.savefig('/Users/josh/Github/scrapers/test.png')
# %%

import spacy
from spacy import displacy
# python3 -m spacy download en_core_web_lg

NER = spacy.load("en_core_web_lg")

def clean_words(labby):
    if any(ele in labby for ele in goog_stems):
        for thing in goog_stems:
            if thing in labby:
                labby = labby.replace(thing, "")
    # labby = labby.replace("'s", '')
    labby = re.sub(r"'s|’s| - ", '', labby)
    # labby = "".join([t for t in labby if ((t.isalpha()) | (t == ' '))])
                # labby = new_string = re.sub(pattern, '', labby)
    labby = labby.strip()
    return labby

print(goog_stems)
def word_frequency(sentences):

    sentence = " ".join(sentences)

    text1= NER(sentence)

    for word in text1.ents:
        if word.label_ == "PERSON":
            if word.text.lower() not in new_stops:
                print(clean_words(word.text),word.label_)

    for word in text1.ents:
        if word.label_ == "ORG":
            if clean_words(word.text) != "":
                if word.text.lower() not in new_stops:
                    print(clean_words(word.text),word.label_)
    # print(text1.ents)

word_frequency(data['Headline'].tolist())
# %%

# %%

import nltk
from nltk import word_tokenize
# nltk.download('averaged_perceptron_tagger')
# nltk.download('universal_tagset')

def word_frequency(sentences):

    sentence = " ".join(sentences)

    tokens = word_tokenize(sentence)
    tags = nltk.pos_tag(tokens, tagset = "universal")
    tag_types = list(set([x[1] for x in tags]))
    print(tag_types)
    print("tags: ", len(tags))
    # nouns = [x[0].lower() for x in tags if x[1] == 'NOUN']
    # print("nouns: ", len(nouns))
    # nouns = [t for t in nouns if t.lower() not in stop_words]
    # print("nouns: ", len(nouns))
    # print(nouns)

    # new_tokens = [t.lower() for t in nouns if t.isalpha()]
    # print("new_tokens: ", len(new_tokens))
    # lemmatizer = WordNetLemmatizer()
    # new_tokens =[lemmatizer.lemmatize(t) for t in new_tokens]
    # print(new_tokens)

    # counted = Counter(new_tokens)

    # word_freq = pd.DataFrame(counted.items(),columns=['word','frequency']).sort_values(by='frequency',ascending=False)

    # return word_freq


data2 = word_frequency(data['Headline'].tolist())

# import seaborn as sns
# import matplotlib.pyplot as plt

# # create subplot of the different data frames
# fig, axes = plt.subplots(figsize=(8,20))

# sns.barplot(ax=axes,x='frequency',y='word',data=data2.head(60))
# plt.savefig('/Users/josh/Github/scrapers/test.png')

# %%
