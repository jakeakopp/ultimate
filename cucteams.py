#!/usr/bin/env python3

# cucteams.py looks at teams from CUC events to identify what teams their
# players played for in other years.

import argparse
import collections
import operator
import os
import re
import requests
import sys
from bs4 import BeautifulSoup

import lib

Franchise = collections.namedtuple('Franchise', ['name', 'url'])

FRANCHISE_URL_TEMPLATE = (
    'https://canadianultimate.com/en_ca/t/%s/roster?division=')

all_players = collections.defaultdict(list)
players_to_franchises = collections.defaultdict(list)
all_teams = collections.defaultdict(list)
all_franchises = collections.defaultdict(list)

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
def load_players_for_franchise(franchise, tsid_cookie):
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
      base_page = lib.download_page(
          base_url, '%s-roster' % url_name, tsid_cookie, tsid_required=True)
    except lib.Error404:
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


def find_past_teams(team, players):
  other_team_counts = collections.defaultdict(int)
  other_franchise_counts = collections.defaultdict(int)
  other_franchise_players = collections.defaultdict(list)
  for player in players:
    for other_team in all_players[player.url]:
      if other_team == team:
        continue
      other_team_counts['%s (%s)' % (other_team.name, other_team.year)] += 1
    #sorted_other_teams = sorted(
    #    other_team_counts.items(), key=operator.itemgetter(1), reverse=True)
    #print("%s top 5 teams: %s" % (team.name, sorted_other_teams[0:5]))

    franchises_covered = [team.name]#url]
    for other_franchise in players_to_franchises[player.url]:
      if other_franchise.name in franchises_covered:
        continue
      franchises_covered.append(other_franchise.name)
      other_franchise_counts[other_franchise.name] += 1
      other_franchise_players[other_franchise.name].append(player.url)

  sorted_other_franchises = sorted(
      other_franchise_counts.items(), key=operator.itemgetter(1), reverse=True)
  top_other_franchise_players = []
  for franchise_name, count in sorted_other_franchises:
    top_other_franchise_players.append(
        (franchise_name, count, other_franchise_players[franchise_name]))
  print("\n%s (%s) top 5 franchises: %s" %
        (team.name, team.year, top_other_franchise_players[0:5]))


def _parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('--years', type=str, default='2019',
                      help='Comma-separated years to print reports for.')
  parser.add_argument(
      '--tsid_cookie', type=str, default='',
      help='tsid cookie value to use to access canadianultimate.com.')

  return parser.parse_args(sys.argv[1:])


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
    lib.process_event(event, year, url, args.tsid_cookie, all_teams, all_players)

  for team in all_teams:
    load_players_for_franchise(
        create_franchise(team.name, team.url), args.tsid_cookie)

  for team, players in all_teams.items():
    if str(team.year) not in args.years.split(','):
      continue
    find_past_teams(team, players)


if __name__ == '__main__':
  main()

