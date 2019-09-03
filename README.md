# Ultimate

## CUC Team History Finder
cucteams.py scrapes the Ultimate Canada website for teams/players that have participated in CUC and determines which teams have most in common with each other.

To run, ensure you have Beautiful Soup 4 installed (pip3 install beatifulsoup4), and run:

`python3 cucteams.py`

For the first run, you will need to pass an additional argument - your login cookie from the CUC website. To get this, log in to canadianultimate.com, then grab the tsid cookie value (in Chrome, go to chrome://settings/cookies/detail?site=canadianultimate.com and grab the "Content" for the tsid cookie). e.g.:

`python3 cucteams.py AwAizIlHh7HmjNWqVEL1ow0VHKk23nqH`

Subsequent runs do not require the cookie because the pages are cached.
