#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib
import itertools
import pandas as pd
import numpy as np

spl = importlib.import_module('scraping.polish')
st = importlib.import_module('stats')
# importlib.reload(spl)

league = 'PlusLiga'
season = 2022


# %% Lists
player_list = spl.fetch_players(league, season)
team_list = spl.fetch_teams(league, season)
match_list = spl.fetch_matches(league, season)


# %% Players
spl.fetch_player_info('PlusLiga', 2022, 2104197)

# Multiple at once
lg = [league]
ids = [30339, 448, 27975]
sns = list(range(season - 1, season + 1))
combs = pd.DataFrame(itertools.product(lg, sns, ids),
                     columns=['League', 'Season', 'PlayerID'])

spl.batch_fetch_player_info(combs)
player_info = spl.batch_fetch_player_info(player_list)


# %% Matches
spl.fetch_match_info('PlusLiga', 2022, 1102401)

# importlib.reload(spl)
combs = match_list
matches = spl.batch_fetch_match_info(combs)
info = matches['information']
stats = matches['stats']


# %% Teams
spl.fetch_team_info('PlusLiga', 2022, 30288)
