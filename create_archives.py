# %%

import os 
from github import Github
from dotenv import load_dotenv
load_dotenv()


# %%


tokeny = os.environ['gitty']

github = Github(tokeny)

repository = github.get_user().get_repo('Archives')


# %%

pathos = 'Archive'

contents = repository.get_contents(pathos)

paths = [x.path.replace(f"{pathos}/", '') for x in contents]



# %%


new = 'tech_meme_top'

if new not in paths:
    # repository.create_file(f'Archive/{new}/test.txt', "test", "hi")
    repository.create_file(f'Archive/{new}/daily_dumps/hi.txt', "test", "hi")
    repository.create_file(f'Archive/{new}/latest.json', "test", "[{'what':'hi'}]")


# %%
