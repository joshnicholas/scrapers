
# %%

import requests
import os 

import pathlib
pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

# %%
init = 'archive'

def already_done(path, stemmo):
    pathos = f"{path}/{stemmo}/daily_dumps"
    fillos = os.listdir(pathos)

    print(fillos)



paths = ['abc_top', 'abs', 'cse', 'foi', 'google', 'graun_top', 'smh_top', 'wiki']

for thing in paths[:1]:
    print(thing)
    already_done(init, thing)

    ## Check whether I have everything first

# archive/abc_top/daily_dumps



# %%

