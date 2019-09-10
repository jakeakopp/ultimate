#!/usr/bin/env python3

import collections
import csv
import os
import requests
from bs4 import BeautifulSoup


CACHEDIR = '/tmp/cuccache'
if not os.path.exists(CACHEDIR):
  os.mkdir(CACHEDIR)
if not os.path.isdir(CACHEDIR):
  exit('Cache dir error.')

Player = collections.namedtuple('Player', ['player_name', 'url', 'gender'])
Team = collections.namedtuple('Team', ['name', 'url', 'year'])
Franchise = collections.namedtuple('Franchise', ['name', 'url'])


class Error404(Exception):
  pass


def download_page(url, cachefilename, tsid_cookie=None, tsid_required=False):
  cachefile = os.path.join(CACHEDIR, cachefilename)
  if os.path.exists(cachefile):
    with open(cachefile) as f:
      contents = f.read()
      if contents == '404':
        raise Error404(url)
      return contents

  print('downloading %s' % url)

  if tsid_required and (tsid_cookie is None or tsid_cookie == ''):
    raise Exception('Specify --tsid_cookie to download pages.')

  cookies = dict()
  if (tsid_cookie is not None) and (tsid_cookie != ''):
    cookies['tsid'] = tsid_cookie

  response = requests.get(url, cookies=cookies)
  if response.status_code == 404:
    with open(cachefile, 'w') as f:
      f.write('404')
    raise Error404
  elif response.status_code != 200:
    raise Exception('url: %s, response: %s' % (url, response))

  contents = response.text
  with open(cachefile, 'w') as f:
    f.write(contents)

  return contents


def load_parsed_data(parsed_data_dir, players_to_teams, teams_to_players,
                     players_to_franchises):
  if players_to_teams is not None:
    # player url to []Team
    with open(os.path.join(parsed_data_dir, 'players_to_teams.csv')) as f:
      reader = csv.reader(f)
      for row in reader:
        if len(row) < 1:
          continue
        player_url = row[0]
        teams = []
        i = 1
        while i < len(row):
          teams.append(Team(row[i], row[i+1], row[i+2]))
          i += 3

        players_to_teams[player_url] = teams

  if teams_to_players is not None:
    # Team to []Player
    with open(os.path.join(parsed_data_dir, 'teams_to_players.csv')) as f:
      reader = csv.reader(f)
      for row in reader:
        if len(row) < 3:
          continue
        team = Team(row[0], row[1], row[2])
        players = []
        i = 3
        while i < len(row):
          players.append(Player(row[i], row[i+1], row[i+2]))
          i += 3

        teams_to_players[team] = players

  if players_to_franchises is not None:
    # player url to set(Franchise)
    with open(os.path.join(parsed_data_dir, 'players_to_franchises.csv')) as f:
      reader = csv.reader(f)
      for row in reader:
        if len(row) < 1:
          continue
        player_url = row[0]
        franchises = []
        i = 1
        while i < len(row):
          franchises.append(Franchise(row[i], row[i+1]))
          i += 2

        players_to_franchises[player_url] = franchises


def process_team(team_div, year, tsid, all_teams, all_players=None):
  team_name = team_div.find_all('h3')[0].get_text()

  player_link_class = (
      'media-item-tile media-item-tile-normal media-item-tile-cover')
  team_url_l = team_div.find_all('a', attrs={'class': player_link_class})
  full_team_url = team_url_l[0].get('href')
  team_url = full_team_url[full_team_url.rfind('/')+1:]
  team = Team(team_name, team_url, year)

  clusters = team_div.find_all(attrs={'class': 'gender-cluster'})
  for cluster in clusters:
    gender = 'F'
    if cluster.find_all('h5')[0].get_text().startswith('Male'):
      gender = 'M'
    players = cluster.find_all('a')
    for player in players:
      player_url = player.get('href')[9:]
      if all_players is not None:
        all_players[player_url].append(team)
      all_teams[team].append(Player(player.text, player_url, gender))

  return team


def process_event(event, year, url, tsid, all_teams, all_players=None):
  pagenum = 1
  # Upper bound of 20 to avoid spamming the site by accident.
  while pagenum < 20:
    requrl = url
    if pagenum > 1:
      requrl += '?page=%d' % pagenum
    print(event, year, requrl)
    contents = download_page(requrl, '%s-%02d' % (event, pagenum), tsid, True)

    soup = BeautifulSoup(contents, "html.parser")

    TEAM_DIV_CLASS = 'span4 media-item-wrapper spacer1'
    team_divs = soup.find_all(attrs={'class': TEAM_DIV_CLASS})
    if len(team_divs) == 0:
      if pagenum == 1:
        exit('No teams found on page %s.' % pagenum)
      print('No more teams on page %d for url "%s".' % (pagenum, url))
      break
    for div in team_divs:
      process_team(div, year, tsid, all_teams, all_players)

    pagenum += 1


