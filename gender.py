#!/usr/bin/env python3

import argparse
import collections
import sys
from bs4 import BeautifulSoup

import lib

def _parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--tsid_cookie', type=str, default='',
      help='tsid cookie value to use to access canadianultimate.com.')

  return parser.parse_args(sys.argv[1:])


class Player(object):
  def __init__(self):
    self.player_name = ''
    self.team_name = ''
    self.gender = ''
    self.stats = Stats()
  def __str__(self):
    return '%s (%s, %s): %s' % (
        self.player_name, self.gender, self.team_name, self.stats)
  def __repr__(self):
    return str(self)

class Stats(object):
  def __init__(self):
    self.assists = 0
    self.goals = 0
  def __str__(self):
    return 'assists: %d, goals: %d' % (self.assists, self.goals)
  def __repr__(self):
    return str(self)


# Map from team to (map of player to stats).
all_teams = dict()


def process_team_game(team_table):
  team_name = team_table.find('b').text
  if team_name not in all_teams:
    print("new team:", team_name)
    all_teams[team_name] = dict()
  team = all_teams[team_name]
  stats_table = team_table.find_all('table')[1]
  # Row 0 is a header.
  header = True
  for row in stats_table.find_all('tr'):
    if header:
      header = False
      continue
    tds = row.find_all('td')
    # Row is: number, player link + name, assists, goals, total points.
    player_name = tds[1].text.strip()
    if player_name not in team:
      team[player_name] = Player()
      team[player_name].player_name = player_name
      team[player_name].team_name = team_name
    team[player_name].stats.assists += int(tds[2].text)
    team[player_name].stats.goals += int(tds[3].text)


def process_game(team1_table, team2_table):
  process_team_game(team1_table)
  process_team_game(team2_table)


def calculate_overall_gender_ratios(all_teams):
  f_goals = 0
  f_assists = 0
  m_goals = 0
  m_assists = 0
  for team in all_teams.values():
    for player in team.values():
      if player.gender == 'F':
        f_goals += player.stats.goals
        f_assists += player.stats.assists
      elif player.gender == 'M':
        m_goals += player.stats.goals
        m_assists += player.stats.assists
      else:
        raise Exception('No gender for player:', player)

  goal_ratio = float(m_goals) / float(f_goals)
  assist_ratio = float(m_assists) / float(f_assists)
  print('f: %s, %s; m: %s, %s\nratio: goals: %s, assists: %s' % (
      f_goals, f_assists, m_goals, m_assists, goal_ratio, assist_ratio))


def get_matching_team(team_name, teams):
  if team_name == '1778':
    team_name = '1778 AT'
  for other_team, players in teams.items():
    if other_team.name.lower() == team_name.lower():
      return players

  raise Exception('didn\'t find:', team_name, teams.keys())


all_not_found_players = []


def get_matching_player(player_name, g_team):
  for g_player in g_team:
    if g_player.player_name.lower() == player_name.lower():
      return g_player

  parts = set(player_name.lower().split())
  match = None
  match_level = 0
  multimatch = []
  for g_player in g_team:
    g_parts = set(g_player.player_name.lower().split())
    isect = g_parts.intersection(parts)
    if len(isect) > match_level:
      match_level = len(isect)
      match = g_player
      multimatch = []
    elif len(isect) == match_level and match_level > 0:
      multimatch = [match, g_player]

  if len(multimatch) > 0:
    raise Exception('multimatch for player %s: %s' % (player_name, multimatch))

  return match
  #raise Exception('did not find %s in %s' % (player_name, g_team))


manual_data = {
'Amélie Bernier-Girard': 'F', # Not on roster, but on 'paid for event' roster.
'Tessa Craig': 'F', # Apparently a coach.
'Heidi Howes': 'F', # Not on roster, but on 'paid for event' roster.
'Craig McFarlane': 'M', # Not on roster, but on 'paid for event' roster.
}


def main():
  args = _parse_args()

  event_url = 'https://frisbee.gravato.eu/cuc2019mix/'
  event_name = 'CUC2019'
  for i in range(1,127):#TODO: end when the teams are ? vs ?
    url = event_url + '?view=gameplay&game=%d' % i
    contents = lib.download_page(url, '%s-stats-%03d' % (event_name, i))

    soup = BeautifulSoup(contents, "html.parser")

    content_div = soup.find('div', attrs={'class': 'content'})
    tds = content_div.table.tr.find_all('td', recursive=False)
    process_game(tds[0], tds[2])

  url_prefix = 'https://canadianultimate.com/en_ca/e/'
  all_teams_g = collections.defaultdict(list)
  lib.process_event('CUC2019', 2019, url_prefix + '2019-cuc-adult-series/teams',
                    args.tsid_cookie, all_teams_g)

  for team_name, team in all_teams.items():
    g_team = get_matching_team(team_name, all_teams_g)
    for player in team.values():
      match = get_matching_player(player.player_name, g_team)
      if match is None:
        if player.player_name in manual_data:
          player.gender = manual_data[player.player_name]
        else:
          all_not_found_players.append((player.player_name, team_name))
      else:
        player.gender = match.gender

  calculate_overall_gender_ratios(all_teams)

  if len(all_not_found_players) > 0:
    print('Failed to find players:', all_not_found_players)

if __name__ == '__main__':
  main()

