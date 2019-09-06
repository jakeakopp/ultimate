#!/usr/bin/env python3

import collections
import os
import requests
from bs4 import BeautifulSoup


CACHEDIR = '/tmp/cuccache'
if not os.path.exists(CACHEDIR):
  os.mkdir(CACHEDIR)
if not os.path.isdir(CACHEDIR):
  exit('Cache dir error.')

Team = collections.namedtuple('Team', ['name', 'url', 'year'])

class Error404(Exception):
  pass


def download_page(url, cachefilename, tsid_cookie=None):
  cachefile = os.path.join(CACHEDIR, cachefilename)
  if os.path.exists(cachefile):
    with open(cachefile) as f:
      contents = f.read()
      if contents == '404':
        raise Error404
      return contents

  print('downloading %s' % url)

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


Player = collections.namedtuple('Player', ['player_name', 'url', 'gender'])


def process_team(team_div, year, tsid, all_teams):
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
      all_teams[team].append(Player(player.text, player_url, gender))


def process_event(event, year, url, tsid, all_teams):
  pagenum = 1
  # Upper bound of 20 to avoid spamming the site by accident.
  while pagenum < 20:
    requrl = url
    if pagenum > 1:
      requrl += '?page=%d' % pagenum
    print(event, year, requrl)
    contents = download_page(requrl, '%s-%02d' % (event, pagenum), tsid)

    soup = BeautifulSoup(contents, "html.parser")

    TEAM_DIV_CLASS = 'span4 media-item-wrapper spacer1'
    team_divs = soup.find_all(attrs={'class': TEAM_DIV_CLASS})
    if len(team_divs) == 0:
      if pagenum == 1:
        exit('No teams found on page %s.' % pagenum)
      print('No more teams on page %d for url "%s".' % (pagenum, url))
      break
    for div in team_divs:
      process_team(div, year, tsid, all_teams)

    pagenum += 1


