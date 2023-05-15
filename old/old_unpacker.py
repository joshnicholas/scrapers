# %%

import os
import pandas as pd 
import json
import dateparser

from sudulunu.helpers import pp

# %%

def proc_old(frame, out, stemmo, pubbo, col_name):
    init = pd.read_csv(frame)

    lenno = len(init)

    counter = 1

    init['Date'] = pd.to_datetime(init['Date'], format="%Y-%m-%d")
    init['Date'] = init['Date'].dt.strftime("%Y_%m_%d")
    # inter['Date'] = inter['Date'].astype(str)



    init['Hour'] = init['Hour'].astype(str)

    init["scraped_datetime"] = init['Date'] + "_" + init['Hour']

    # pp(init)

    for timmo in init["scraped_datetime"].unique().tolist():

        inter = init.loc[init["scraped_datetime"] == timmo].copy()
        inter.drop(columns={'What', 'Date', 'Hour', "scraped_datetime"}, inplace=True)


        tee = inter.T.reset_index()

        second = tee.columns.tolist()[1]

        tee.rename(columns={'index': "Rank", second: col_name}, inplace=True)
        tee['publication'] = pubbo
        tee["scraped_datetime"] = timmo

        tee.dropna(inplace=True)

        # pp(tee)
        # print(tee.columns.tolist())

        jsony = tee.to_dict(orient='records')
        content = json.dumps(jsony)


        with open(f"{out}/{stemmo}/daily_dumps/{timmo}.json", "w") as f:
            json.dump(content, f)

        if counter % 10 == 0:
            print(tee.columns.tolist())
            print(f"{counter}/{lenno}")

        counter += 1

        # pp(tee)

# proc_old('/Users/josh_nicholas/Personal/trends/data/abc_pop.csv','/Users/josh_nicholas/Personal/Archives/Archive' ,'abc_top', 'ABC', 'Headline')


# proc_old('/Users/josh_nicholas/Personal/trends/data/Aus_google_trends.csv','/Users/josh_nicholas/Personal/Archives/Archive' ,'google', 'google',  "Search")

# proc_old('/Users/josh_nicholas/Personal/trends/data/smh_pop.csv','/Users/josh_nicholas/Personal/Archives/Archive' ,'smh_top', 'SMH', 'Headline')

# proc_old('/Users/josh_nicholas/Personal/trends/data/tech_meme_pop.csv' ,'/Users/josh_nicholas/Personal/Archives/Archive','tech_meme_top', 'Tech Meme', 'Headline')

# %%

def proc_wiki(frame, out, stemmo, pubbo, col_name):
    init = pd.read_csv(frame)

    lenno = len(init)

    counter = 1

    for timmo in init["UTC Date"].unique().tolist():

        inter = init.loc[init["UTC Date"] == timmo].copy()
        inter.drop(columns={'What', "UTC Date"}, inplace=True)


        tee = inter.T.reset_index()

        second = tee.columns.tolist()[1]

        tee.rename(columns={'index': "Rank", second: col_name}, inplace=True)
        tee['publication'] = pubbo
        tee["scraped_datetime"] = timmo

        tee.dropna(inplace=True)

        # pp(tee)
        # print(tee.columns.tolist())

        jsony = tee.to_dict(orient='records')
        content = json.dumps(jsony)


        with open(f"{out}/{stemmo}/daily_dumps/{timmo}.json", "w") as f:
            json.dump(content, f)

        if counter % 10 == 0:
            print(tee.columns.tolist())
            print(f"{counter}/{lenno}")

        counter += 1

# proc_wiki('/Users/josh_nicholas/Personal/trends/data/wiki_trends.csv' ,'/Users/josh_nicholas/Personal/Archives/Archive','wiki', 'wiki', 'Trend')
# %%


def unpack_cse(frame, out, stemmo):
    init = pd.read_csv(frame)

    lenno = len(init)

    

    counter = 1

    # pp(init)

    for timmo in init["Date"].unique().tolist():

        parsed = dateparser.parse(timmo)
        # print(parsed)
        datto = parsed.strftime("%Y_%m_%d")

        # print(datto)

        inter = init.loc[init["Date"] == timmo].copy()
        # pp(inter)
        inter.drop(columns={ "Date"}, inplace=True)



        jsony = inter.to_dict(orient='records')
        content = json.dumps(jsony)


        with open(f"{out}/{stemmo}/daily_dumps/{datto}.json", "w") as f:
            json.dump(content, f)

        if counter % 50 == 0:
            print(inter.columns.tolist())
            print(f"{counter}/{lenno}")

        counter += 1

unpack_cse('/Users/josh_nicholas/Personal/cse_scrape/archive/cse.csv' ,'/Users/josh_nicholas/Personal/Archives/Archive','cse')
# %%
