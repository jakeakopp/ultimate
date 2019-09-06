#!/usr/bin/env python3

import argparse
import collections
import operator
import os
import re
import requests
import sys
from bs4 import BeautifulSoup

Franchise = collections.namedtuple('Franchise', ['name', 'url'])
Team = collections.namedtuple('Team', ['name', 'url', 'year'])

FRANCHISE_URL_TEMPLATE = (
    'https://canadianultimate.com/en_ca/t/%s/roster?division=')

CACHEDIR = '/tmp/cuccache'
if not os.path.exists(CACHEDIR):
  os.mkdir(CACHEDIR)
if not os.path.isdir(CACHEDIR):
  exit('Cache dir error.')

all_players = collections.defaultdict(list)
players_to_franchises = collections.defaultdict(list)
all_teams = collections.defaultdict(list)
all_franchises = collections.defaultdict(list)


def download_page(url, cachefilename, args):
  cachefile = os.path.join(CACHEDIR, cachefilename)
  if os.path.exists(cachefile):
    with open(cachefile) as f:
      contents = f.read()
      if contents == '404':
        raise Error404
      return contents

  if args.tsid_cookie == '':
      sys.exit('Specify --tsid_cookie to download pages.')

  print('downloading %s' % url)

  cookies = dict(tsid=args.tsid_cookie)
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


PLAYER_LINK_CLASS = (
    'media-item-tile media-item-tile-small media-item-tile-cover')

def create_franchise(name, url):
  # Match anything ending in a dash and one or two digits.
  m = re.match('(.*)-\d\d?$', url)
  if m is None:
    return Franchise(name, url)
  return Franchise(name, m.group(1))



# There are often multiple "different" teams which are the same team in
# different years. e.g. union, union-1, ..., union-8 are all the same.
# However, union-9 and union-10 are actually different.
# So we download all "-%d"-suffixed versions of the team and assume they
# are the same team. If they truly are a different team, there shouldn't
# be much if any overlap so the results won't be affected.
def load_players_for_franchise(franchise, args):
  if len(all_franchises[franchise]) > 0:
    return

  i = 0
  # Upper bound of 30 to avoid spamming the site by accident.
  # Note that there are 28 different registrations for "Phoenix".
  while i < 30:
    url_name = franchise.url
    if i > 0:
      url_name += '-%d' % i
    base_url = FRANCHISE_URL_TEMPLATE % url_name
    base_page = None
    try:
      base_page = download_page(base_url, '%s-roster' % url_name, args)
    except Error404:
      #print('Didn\'t find more rosters at', url_name)
      break

    soup = BeautifulSoup(base_page, "html.parser")
    rows = soup.find_all('div', attrs={'class': 'row-fluid'})
    for row in rows:
      for player_soup in row.find_all('a', attrs={'class': PLAYER_LINK_CLASS}):
        player_name = player_soup.get('href')[9:]
        players_to_franchises[player_name].append(franchise)

    i += 1

  all_franchises[franchise] = 'processed'


def process_team(team_div, year, args):
  team_name = team_div.find_all('h3')[0].get_text()

  player_link_class = (
      'media-item-tile media-item-tile-normal media-item-tile-cover')
  team_url_l = team_div.find_all('a', attrs={'class': player_link_class})
  full_team_url = team_url_l[0].get('href')
  team_url = full_team_url[full_team_url.rfind('/')+1:]
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

  load_players_for_franchise(create_franchise(team_name, team_url), args)


def find_past_teams(team, players):
  other_team_counts = collections.defaultdict(int)
  other_franchise_counts = collections.defaultdict(int)
  other_franchise_players = collections.defaultdict(list)
  for player_name in players:
    for other_team in all_players[player_name]:
      if other_team == team:
        continue
      other_team_counts['%s (%s)' % (other_team.name, other_team.year)] += 1
    #sorted_other_teams = sorted(
    #    other_team_counts.items(), key=operator.itemgetter(1), reverse=True)
    #print("%s top 5 teams: %s" % (team.name, sorted_other_teams[0:5]))

    franchises_covered = [team.name]#url]
    for other_franchise in players_to_franchises[player_name]:
      if other_franchise.name in franchises_covered:
        continue
      franchises_covered.append(other_franchise.name)
      other_franchise_counts[other_franchise.name] += 1
      other_franchise_players[other_franchise.name].append(player_name)

  sorted_other_franchises = sorted(
      other_franchise_counts.items(), key=operator.itemgetter(1), reverse=True)
  top_other_franchise_players = []
  for franchise_name, count in sorted_other_franchises:
    top_other_franchise_players.append(
        (franchise_name, count, other_franchise_players[franchise_name]))
  print("\n%s (%s) top 5 franchises: %s" %
        (team.name, team.year, top_other_franchise_players[0:5]))


class Error404(Exception):
  pass


def _parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('--years', type=str, default='2019',
                      help='Comma-separated years to print reports for.')
  parser.add_argument(
      '--tsid_cookie', type=str, default='',
      help='tsid cookie value to use to access canadianultimate.com.')

  return parser.parse_args(sys.argv[1:])


def process_event(event, year, url):
  pagenum = 1
  # Upper bound of 20 to avoid spamming the site by accident.
  while pagenum < 20:
    requrl = url
    if pagenum > 1:
      requrl += '?page=%d' % pagenum
    print(event, year, requrl)
    contents = download_page(requrl, '%s-%02d' % (event, pagenum), args)

    soup = BeautifulSoup(contents, "html.parser")

    TEAM_DIV_CLASS = 'span4 media-item-wrapper spacer1'
    team_divs = soup.find_all(attrs={'class': TEAM_DIV_CLASS})
    if len(team_divs) == 0:
      if pagenum == 1:
        exit('No teams found on page %s.' % pagenum)
      print('No more teams on page %d for url "%s".' % (pagenum, url))
      break
    for div in team_divs:
      process_team(div, year, args)

    pagenum += 1


#TODO: URLs for other tournaments? University? 4s?
url_prefix = 'https://canadianultimate.com/en_ca/e/'
urls = [
('CUC2019', 2019, url_prefix + '2019-cuc-adult-series/teams'),
('CUC2018', 2018, url_prefix + 'cuc-2018-series/teams'),
('CUC2017', 2017, url_prefix + 'cuc-series/teams'),
('CUCM2016', 2016, url_prefix + 'cuc-mixed-2016/teams'),
('CUC2016', 2016, url_prefix + 'cuc-2016/teams'),
('CUC2015', 2015, url_prefix + '2015-canadian-ultimate-championships/teams'),
# TODO: For 2014, rosters are not listed on the main page. Need to go to:
# https://canadianultimate.com/en_ca/t/TEAMNAME/roster?division=4316
# for each team and parse those pages.
# However, scraping this URL still causes the rosters to be populated for any
# "franchises" that didn't participate in any of the other events.
('CUC2014', 2014, url_prefix + '2014-cuc-seriesadult/teams')
]
def main():
  args = _parse_args()

  for event, year, url in urls:
    process_event(event, year, url)

  for team, players in all_teams.items():
    if str(team.year) not in args.years.split(','):
      continue
    find_past_teams(team, players)


if __name__ == '__main__':
  main()

