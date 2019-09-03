#!/usr/bin/env python3

# requires bs4: pip3 install beautifulsoup4

import collections
import os
import requests
import sys
from bs4 import BeautifulSoup


all_players = collections.defaultdict(list)
all_teams = collections.defaultdict(list)


def process_team(team_div, year):
  team_name = team_div.find_all('h3')[0].get_text()
  team_w_year = '%s (%s)' % (team_name, year)
  print(team_name)

  clusters = team_div.find_all(attrs={'class': 'gender-cluster'})
  for cluster in clusters:
    gender = 'female'
    if cluster.find_all('h5')[0].get_text().startswith('Male'):
      gender = 'male'
    print('gender:', gender)
    players = cluster.find_all('a')
    for player in players:
      player_name = player.get('href')[9:]
      print(player_name)
      all_players[player_name].append(team_w_year)
      all_teams[team_w_year].append(player_name)


contents = ''
cachedir = '/tmp/cuccache'
if not os.path.exists(cachefile):
  os.mkdir(cachedir)
if not os.path.isdir(cachedir):
  exit('Cache dir error.')

cachefile = '/tmp/cuccache'
if os.path.exists(cachefile):
  with open(cachefile) as f:
    contents = f.read()

urls = [
(2019, 'https://canadianultimate.com/en_ca/e/2019-cuc-adult-series/teams')
]
for year, url in urls:
  print(year, url)

  if len(contents) < 5:
    if len(sys.argv) < 2:
      sys.exit('Required argument: tsid cookie token')

  #TODO: URLs for other years / tournaments.
  #TODO: ?page=N until it fails
  cookies = dict(tsid=sys.argv[1])
  response = requests.get(url, cookies=cookies)
  print(response)
  contents = response.text
  with open(cachefile, 'w') as f:
    f.write(contents)

  soup = BeautifulSoup(contents, "html.parser")

  TEAM_DIV_CLASS = 'span4 media-item-wrapper spacer1'
  team_divs = soup.find_all(attrs={'class': TEAM_DIV_CLASS})
  for div in team_divs:
    process_team(div, year)

  print(all_players)
