import pathlib
import os 
pathos = pathlib.Path(__file__).parent.parent
os.chdir(pathos)
# print(os.getcwd())
import time

do = []
do.extend(list(pathlib.Path('trend_scrapers').rglob("*.py")))
do.extend(list(pathlib.Path('top_story_scrapers').rglob("*.py")))

for scraper in do:
    print("Running: ", str(scraper))
    os.system(f"python3 {str(scraper)}")
    time.sleep(1)
