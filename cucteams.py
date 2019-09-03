#!/usr/bin/env python3

# requires bs4: pip3 install beautifulsoup4

import collections
import operator
import os
import requests
import sys
from bs4 import BeautifulSoup

Team = collections.namedtuple('Team', ['name', 'url', 'year'])

all_players = collections.defaultdict(list)
all_teams = collections.defaultdict(list)


def process_team(team_div, year):
  team_name = team_div.find_all('h3')[0].get_text()
  team_url_l = team_div.find_all('a', attrs={'class': 'media-item-tile media-item-tile-normal media-item-tile-cover'})
  team_url = team_url_l[0].get('href')[9:]
  team = Team(team_name, team_url, year)

  clusters = team_div.find_all(attrs={'class': 'gender-cluster'})
  for cluster in clusters:
    gender = 'female'
    if cluster.find_all('h5')[0].get_text().startswith('Male'):
      gender = 'male'
    players = cluster.find_all('a')
    for player in players:
      player_name = player.get('href')[9:]
      all_players[player_name].append(team)
      all_teams[team].append(player_name)


def find_past_teams(team, players):
  other_team_counts = collections.defaultdict(int)
  other_franchise_counts = collections.defaultdict(int)
  other_franchise_players = collections.defaultdict(list)
  for player_name in players:
    franchises_covered = [team.name]
    for other_team in all_players[player_name]:
      if other_team == team:
        continue
      other_team_counts['%s (%s)' % (other_team.name, other_team.year)] += 1
      if other_team.name in franchises_covered:
        continue
      franchises_covered.append(other_team.name)
      other_franchise_counts[other_team.name] += 1
      other_franchise_players[other_team.name].append(player_name)

  #sorted_other_teams = sorted(
  #    other_team_counts.items(), key=operator.itemgetter(1), reverse=True)
  #print("%s top 5 teams: %s" % (team.name, sorted_other_teams[0:5]))

  sorted_other_franchises = sorted(
      other_franchise_counts.items(), key=operator.itemgetter(1), reverse=True)
  top_other_franchise_players = []
  for franchise_name, count in sorted_other_franchises:
    top_other_franchise_players.append(
        (franchise_name, count, other_franchise_players[franchise_name]))
  print("%s (%s) top 5 franchises: %s" % (team.name, team.year, top_other_franchise_players[0:5]))

cachedir = '/tmp/cuccache'
if not os.path.exists(cachedir):
  os.mkdir(cachedir)
if not os.path.isdir(cachedir):
  exit('Cache dir error.')

#TODO: URLs for other tournaments? University? 4s?
url_prefix = 'https://canadianultimate.com/en_ca/e/'
urls = [
('CUC2019', 2019, url_prefix + '2019-cuc-adult-series/teams'),
('CUC2018', 2018, url_prefix + 'cuc-2018-series/teams'),
('CUC2017', 2017, url_prefix + 'cuc-series/teams'),
('CUCM2016', 2016, url_prefix + 'cuc-mixed-2016/teams'),
('CUC2016', 2016, url_prefix + 'cuc-2016/teams'),
('CUC2015', 2015, url_prefix + '2015-canadian-ultimate-championships/teams')
# TODO: For 2014, rosters are not listed on the main page. Need to go to:
# https://canadianultimate.com/en_ca/t/TEAMNAME/roster?division=4316
# for each team and parse those pages.
#('CUC2014', 2014, url_prefix + '2014-cuc-seriesadult/teams')
]
for event, year, url in urls:
  print(event, year, url)

  pagenum = 1
  while pagenum < 20:
    contents = ''
    cachefile = os.path.join(cachedir, '%s-%02d' % (event, pagenum))
    if os.path.exists(cachefile):
      with open(cachefile) as f:
        contents = f.read()

    if len(contents) == 0:
      if len(sys.argv) < 2:
        sys.exit('Required argument: tsid cookie token')

      cookies = dict(tsid=sys.argv[1])
      requrl = url
      print('downloading page %s' % pagenum)
      if pagenum > 1:
        requrl += '?page=%d' % pagenum
      response = requests.get(requrl, cookies=cookies)
      if response.status_code != 200:
        sys.exit('Error: %s' % response)
      contents = response.text
      with open(cachefile, 'w') as f:
        f.write(contents)

    soup = BeautifulSoup(contents, "html.parser")

    TEAM_DIV_CLASS = 'span4 media-item-wrapper spacer1'
    team_divs = soup.find_all(attrs={'class': TEAM_DIV_CLASS})
    if len(team_divs) == 0:
      if pagenum == 1:
        exit('No teams found on page %s.' % pagenum)
      print('No more teams on page %d for url "%s".' % (pagenum, url))
      break
    for div in team_divs:
      process_team(div, year)

    pagenum += 1

for team, players in all_teams.items():
  find_past_teams(team, players)

