import pathlib
import os 
pathos = pathlib.Path(__file__).parent.parent
os.chdir(pathos)
# print(os.getcwd())
import time

do = []
do.extend(list(pathlib.Path('foi_scrapers').rglob("*.py")))

exclude = []

for scraper in do:
    if str(scraper) not in exclude:
        print("Running: ", str(scraper))
        os.system(f"python3 {str(scraper)}")
        time.sleep(1)
