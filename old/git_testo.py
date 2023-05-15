# %%

from github import Github, UnknownObjectException

from dotenv import load_dotenv
load_dotenv()
import os 


# %%


stemmo = "2023_05_15_20"
repo = 'Archives'
what = 'tech_meme_top'

tokeny = os.environ['gitty']

github = Github(tokeny)

repository = github.get_user().get_repo(repo)


filename = f'Archive/{what}/daily_dumps/{stemmo}.json'
# latest = f'Archive/{what}/latest.json'

contents = repository.get_contents(filename)

def try_file(pathos):
    try:
        repository.get_contents(pathos)
        return True
    except UnknownObjectException as e:
        return False
    
exists = try_file(filename)

print(exists)
# %%
