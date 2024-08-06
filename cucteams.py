#!/usr/bin/env python3

# cucteams.py looks at teams from CUC events to identify what teams their
# players played for in other years.

import argparse
import collections
import csv
import operator
import os
import re
import sys
from bs4 import BeautifulSoup

import lib

FRANCHISE_URL_TEMPLATE = (
    'https://canadianultimate.com/en_ca/t/%s/roster?division=')
PLAYER_LINK_CLASS = (
    'media-item-tile media-item-tile-small media-item-tile-cover')

processed_franchises = dict()


def create_franchise(name, url):
  # Match anything ending in a dash and one or two digits.
  # TODO: Exception for 'dinner-at-4'.
  m = re.match('(.*)-\d\d?$', url)
  if m is None:
    return lib.Franchise(name, url)
  return lib.Franchise(name, m.group(1))


# There are often multiple "different" teams which are the same team in
# different years. e.g. union, union-1, ..., union-8 are all the same.
# However, union-9 and union-10 are actually different.
# So we download all "-%d"-suffixed versions of the team and assume they
# are the same team. If they truly are a different team, there shouldn't
# be much if any overlap so the results won't be affected.
def load_players_for_franchise(franchise, players_to_franchises, tsid_cookie):
  if franchise in processed_franchises:
    return

  i = 0
  have_results = False
  # Upper bound of 30 to avoid spamming the site by accident.
  # Note that there are 28 different registrations for "Phoenix".
  while i < 30:
    url_name = franchise.url
    if i > 0:
      url_name += '-%d' % i
    url = FRANCHISE_URL_TEMPLATE % url_name
    page = None
    try:
      page = lib.download_page(
          url, '%s-roster' % url_name, tsid_cookie, tsid_required=True)
    except lib.Error404:
      if not have_results:
        # Some teams (e.g. BoD) don't have a version without a -N suffix. Some
        # (Firefly) doen't have -1 either. Just ignore 404s until we've actually
        # got something.
        i += 1
        continue
      break

    have_results = True

    soup = BeautifulSoup(page, "html.parser")
    rows = soup.find_all('div', attrs={'class': 'row-fluid'})
    for row in rows:
      for player_soup in row.find_all('a', attrs={'class': PLAYER_LINK_CLASS}):
        player_url = player_soup.get('href')[9:]
        players_to_franchises[player_url].add(franchise)

    i += 1

  if not have_results:
    raise Exception('Got no rosters for franchise %s' % franchise.url)

  processed_franchises[franchise] = 'processed'


all_not_found_players = []


def find_past_teams(team, players, players_to_teams, players_to_franchises):
  other_team_counts = collections.defaultdict(int)
  other_franchise_counts = collections.defaultdict(int)
  other_franchise_players = collections.defaultdict(list)
  for player in players:
    for other_team in players_to_teams[player.url]:
      if other_team == team:
        continue
      other_team_counts['%s (%s)' % (other_team.name, other_team.year)] += 1
    #sorted_other_teams = sorted(
    #    other_team_counts.items(), key=operator.itemgetter(1), reverse=True)
    #print("%s top 5 teams: %s" % (team.name, sorted_other_teams[0:5]))

    franchises_covered = [team.name]
    if player.url not in players_to_franchises:
      all_not_found_players.append(player.url)
      continue
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
  s = []
  for franchise_name, count, players in top_other_franchise_players[0:5]:
    s.append('%s (%s): %s  ' % (franchise_name, count, ', '.join(players)))
  print("\n%s (%s) top 5 franchises:  \n%s" % (
      team.name, team.year, '  \n'.join(s)))


def _parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('--years', type=str, default='2023',
                      help='Comma-separated years to print reports for.')
  parser.add_argument(
      '--tsid_cookie', type=str, default='',
      help='tsid cookie value to use to access canadianultimate.com.')
  parser.add_argument(
      '--parsed_data_dir', type=str, default='parsed_data',
      help='Directory containing the data, already downloaded and parsed.')

  return parser.parse_args(sys.argv[1:])


def write_parsed_data(parsed_data_dir, players_to_teams, teams_to_players,
                      players_to_franchises):
  if not os.path.exists(parsed_data_dir):
    os.makedirs(parsed_data_dir)

  # player url to []lib.Team
  with open(os.path.join(parsed_data_dir, 'players_to_teams.csv'), 'w') as f:
    writer = csv.writer(f)
    for player_url, teams in players_to_teams.items():
      row = [player_url]
      for team in sorted(teams, key=lambda t: t.name+t.url+str(t.year)):
        row += [team.name, team.url, team.year]
      writer.writerow(row)

  # lib.Team to []lib.Player
  with open(os.path.join(parsed_data_dir, 'teams_to_players.csv'), 'w') as f:
    writer = csv.writer(f)
    for team, players in teams_to_players.items():
      row = [team.name, team.url, team.year]
      for player in players:
        row += [player.player_name, player.url, player.gender]
      writer.writerow(row)

  # player url to []lib.Franchise
  with open(os.path.join(parsed_data_dir, 'players_to_franchises.csv'), 'w') as f:
    writer = csv.writer(f)
    for player_url, franchises in players_to_franchises.items():
      row = [player_url]
      for franchise in sorted(franchises, key=lambda f: f.name+f.url):
        row += [franchise.name, franchise.url]
      writer.writerow(row)


#TODO: URLs for other tournaments? University? 4s?
url_prefix = 'https://canadianultimate.com/en_ca/e/'
urls = [
('CUC_Masters_2024', 2024, url_prefix + '2024-cuc-series-masters/teams'),
('CUC_2024', 2024, url_prefix + '2024-cuc-series-senior/teams'),
('CUC_Masters_2023', 2023, url_prefix + '2023-cuc-masters/teams'),
('CUC_2023', 2023, url_prefix + '2023-cuc-series-senior/teams'),
('CUC_Masters_2022', 2022, url_prefix + '2022-cuc-masters/teams'),
('CUC_2022', 2022, url_prefix + '2022-cuc-seniors/teams'),
('UC_Invite_2021', 2021, url_prefix + 'uc-invitational-senior/teams'),
('UC_Invite_2021_Masters', 2021, url_prefix + 'uc-invitational-masters/teams'),
('CUC2019', 2019, url_prefix + '2019-cuc-adult-series/teams'),
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

  all_teams = collections.defaultdict(list)
  all_players = collections.defaultdict(list)
  players_to_franchises = collections.defaultdict(set)

  if args.parsed_data_dir and os.path.exists(args.parsed_data_dir):
    print('Loading pre-parsed data from %s.' % args.parsed_data_dir)
    lib.load_parsed_data(
        args.parsed_data_dir, all_players, all_teams, players_to_franchises)
  else:
    for event, year, url in urls:
      lib.process_event(event, year, url, args.tsid_cookie, all_teams, all_players)

    for team, players in all_teams.items():
      franchise = create_franchise(team.name, team.url)
      # For some reason certain players appear on the roster for the event, but
      # not on the "all time" roster. None of these seem to appear on the stats
      # site, so they're probably not relevant, but we include them here for
      # completeness.
      for player in players:
        players_to_franchises[player.url].add(franchise)
      # Load the rest of the players from the "all time" roster.
      load_players_for_franchise(franchise, players_to_franchises, args.tsid_cookie)

    write_parsed_data(args.parsed_data_dir, all_players, all_teams,
                      players_to_franchises)

  for team, players in all_teams.items():
    if str(team.year) not in args.years.split(','):
      continue
    find_past_teams(team, players, all_players, players_to_franchises)

  if all_not_found_players:
    print('Failed to find some players on any franchise: %s' % all_not_found_players)


if __name__ == '__main__':
  main()

