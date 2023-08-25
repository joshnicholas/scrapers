# %%

import os 
from github import Github
from dotenv import load_dotenv
load_dotenv()



tokeny = os.environ['gitty']

github = Github(tokeny)

repository = github.get_user().get_repo('Archives')
# %%

### For new foi folders

def create_repo_directories(pathos, stemmo):


    contents = repository.get_contents(pathos)

    paths = [x.path.replace(f"{pathos}/", '') for x in contents]

    print(paths)

    ## For new folders entirely

    if stemmo not in paths:
        # repository.create_file(f'{pathos}/{new}/test.txt', "test", "hi")
        repository.create_file(f'{pathos}/{stemmo}/daily_dumps/hi.txt', "test", "hi")
        repository.create_file(f'{pathos}/{stemmo}/latest.json', "test", "[{'what':'hi'}]")

# create_repo_directories('Archive', 'aus_visa_wait')
# create_repo_directories('Archive', 'journalism')
# create_repo_directories('Archive', 'link-log')
create_repo_directories('Archive', 'headlines')
# %%

# thingo = 'attorney_general'
# repository.create_file(f'Archive/foi/inter/{thingo}.json', "test", "[{'what':'hi'}]")