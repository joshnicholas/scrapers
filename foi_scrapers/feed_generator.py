# %%
import pandas as pd 

import os 
import pathlib

import datetime
import pytz
import json 

from jsonfeedvalidator import validate_feed, format_errors, ErrorTree

pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

print("cwd: ", os.getcwd())

def json_feed_dumper(out_path, file_name, frame):

    copier = frame.copy()
    # copier['Date'] = pd.to_datetime(copier['Date'], format='%Y-%m-%d')
    # copier['Date'] = copier['Date'].dt.isoformat
    dicto = {
            "version": "https://jsonfeed.org/version/1",
            "title": "Foi disclosures",
            "feed_url": "https://github.com/joshnicholas/oz-foi-disclosure-logs/blob/c68876607d8f95e3fc84d1e583105c658ce491e3/feeds/feed.json",
            # "home_page_url": "https:/joshnicholas.com"
             }

    items = []
    copier = copier[:1]
    for index,row in copier.iterrows():
        record = {
            "id": row['Id'],
            "content_text": row['Title'],
            "url": row['File'],
            "date_published": row['Date'],
            "author": {
                "name": row['Agency'],
                "url": row['Home_url']
            }
        }
        items.append(record)
    
    dicto['items'] = items

    # print(dicto)

        # print(row)

    jsony = json.dumps(dicto)
    errors = validate_feed(jsony)
    formatted = format_errors(jsony, ErrorTree(errors))

    print(formatted)
    # print(errors)


    with open(f"{out_path}/{file_name}.json", 'w') as f:
       json.dump(dicto, f)

# %%

today = datetime.datetime.now()
scrape_date_stemmo = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y%m%d')

# %%

fillos = os.listdir('../data/foi')
fillos = [x for x in fillos if ".csv" in x]

# print(fillos)

listo = []
for fillo in fillos:
    inter = pd.read_csv(f'../data/foi/{fillo}')
    listo.append(inter)

cat = pd.concat(listo)

cat['Date'] = pd.to_datetime(cat['Date'], format='%Y-%m-%d')
cat.sort_values(by=['Date'], ascending=False, inplace=True)
cat['Date'] = cat['Date'].dt.strftime('%Y-%m-%d')

cat.fillna('', inplace=True)

# print(cat)
# print(cat.columns.tolist())

with open(f'../archive/foi/{scrape_date_stemmo}.csv', 'w') as f:
    cat.to_csv(f, index=False, header=True)

with open(f'../archive/latest.csv', 'w') as f:
    cat.to_csv(f, index=False, header=True)

with open(f'../static/latest_foi.csv', 'w') as f:
    cat.to_csv(f, index=False, header=True)

# json_feed_dumper('feeds', 'feed', cat)




# %%



# %%


### This was the old version when I was making an rss feed
# from feedgen.feed import FeedGenerator

# fillos = os.listdir('data')
# fillos = [x for x in fillos if ".csv" in x]

# print(fillos)


# for fillo in fillos:
#     inter = pd.read_csv(f'data/{fillo}')

#     agency = inter['Agency'].values[0]
#     urlo = ''.join(inter['File'].values[0].split('/')[:3])

#     stemmo = fillo.replace(".csv", "")


    # with open('')

#     # print(agency)
#     # print(urlo)

#     fg = FeedGenerator()

#     fg.id(agency)
#     fg.title(f'{agency} FOI')
#     fg.link( href=urlo)

#     fg.language('en')

#     for index,row in inter.iterrows():

#         datto = datetime.datetime.strptime(row['Date'], "%Y-%m-%d")
#         datto = datto.astimezone(pytz.timezone('Australia/Sydney'))

#         fe = fg.add_entry()
#         fe.id(str(row['Id']))
#         fe.title(row['Title'])
#         fe.link(href=row['File'])
#         fe.pubDate(datto)
#         fe.updated(datto)
#         # fe.description(objecto['summary'])

#     fg.atom_file(f'feeds/{stemmo}.xml')
# # %%
