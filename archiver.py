
# %%

import requests
import os 
import shutil
import pandas as pd 

import pathlib
pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

# %%
init = 'archive'

def already_done(path, stemmo):
    pathos = f"{path}/{stemmo}/daily_dumps"
    fillos = os.listdir(pathos)
    fillos = [x.strip() for x in fillos]

    # print(fillos)
    return fillos

paths = ['abs','foi', 'abc_top', 'cse', 'google', 'graun_top', 'smh_top', 'wiki']

for thing in paths[:1]:
    print(thing)
    donners = already_done(init, thing)

    print("already done: ", donners)

    r = requests.get(f'https://thambili.herokuapp.com/check_archives?folder={thing}')
    # r = requests.get(f"http://127.0.0.1:5000/check_archives?folder={thing}")

    appy = r.text.split(",")

    print("In app: ", appy)

    # diff = [x for x in appy if (x.strip() not in donners) & (x != ' ')]
    # # diff = ['202305.csv']

    # print("Diff: ", diff)

    # if len(diff) > 0:
    #     for fillo in diff:
    #         print(fillo)
    #         stemmo = fillo.replace(".csv", '')
    #         stemmo = stemmo.strip()

    #         response = requests.get(f"https://thambili.herokuapp.com/get_archives?pathos={thing}&file={stemmo}", stream=True)

    #         with open(f"{init}/{thing}/daily_dumps/{fillo}", "wb") as file:
    #             for chunk in response.iter_content(chunk_size=8192):
    #                 file.write(chunk)
    #             file.flush()


# %%
