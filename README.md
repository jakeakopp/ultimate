# Ultimate

## CUC Team History Finder
cucteams.py scrapes the Ultimate Canada website for teams/players that have participated in CUC and determines which teams have most in common with each other.

To run, ensure you have the requirements installed (`pip3 install -r requirements.txt`), and run:

`python3 cucteams.py`

You may want to use a virtual environment, e.g.:

`python -m venv .`

`source bin/activate`

By default, this will use the data in the parsed_data/ directory. If you wish to regenerate this data, you can delete it and re-run the script. In this case, you will need to pass an additional argument - your login cookie from the CUC website. To get this, log in to canadianultimate.com, then grab the tsid cookie value (in Chrome, go to chrome://settings/cookies/detail?site=canadianultimate.com and grab the "Content" for the tsid cookie). e.g.:

`python3 cucteams.py --tsid_cookie AwAizIlHh7HmjNWqVEL1ow0VHKk23nqH`

Subsequent runs do not require the cookie because the pages are cached. Note that attempting to download everything in one run will likely trigger rate-limiting from canadianultimate.com. If this happens, the cache will persist, so you can just wait a minute and re-run to get further each time this happens.

Pre-computed results for 2023 at [teams_2023.md](teams_2023.md).

## CUC Gender Scoring Ratios
gender.py scrapes the Ultimate Canada website for genders, scrapes the stats website for stats, and calculates the ratios of points that were thrown/caught by male/female players.

Pre-computed results for 2019 at [gender.md](gender.md).
