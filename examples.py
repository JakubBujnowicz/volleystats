#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib
import itertools
import pandas as pd
import numpy as np

spl = importlib.import_module('scraping.polish')
# importlib.reload(spl)
st = importlib.import_module('stats')

league = 'PlusLiga'
season = 2022


# %% Lists
player_list = spl.fetch_players(league, season)
team_list = spl.fetch_teams(league, season)
match_list = spl.fetch_matches(league, season)


# %% Players
player_ex = spl.fetch_player_info(league, season, 2104197)
player_ex

# Multiple at once
lg = [league]
ids = [30339, 448, 27975]
sns = list(range(season - 1, season + 1))
combs = pd.DataFrame(itertools.product(lg, sns, ids),
                     columns=['League', 'Season', 'PlayerID'])

player_info = spl.batch_fetch_player_info(combs)
player_info = spl.batch_fetch_player_info(player_list)


# %% Matches
match_ex = spl.fetch_match_info(league, season, 1102401)
match_ex

matches = spl.batch_fetch_match_info(match_list)
m_info = matches['information']
m_stats = matches['stats']
m_results = matches['results']


# %% Teams
team_ex = spl.fetch_team_info(league, season, 30288)
team_ex

teams = spl.batch_fetch_team_info(team_list)
t_info = teams['information']
t_roster = teams['roster']
