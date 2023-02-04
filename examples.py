#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib
import itertools
import pandas as pd
import numpy as np

spl = importlib.import_module('scraping.polish')
importlib.reload(spl)

league = 'PlusLiga'
season = 2021


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
combs = pd.DataFrame(itertools.product(lg, sns, ids))

spl.batch_fetch_player_info(combs)
# spl.batch_fetch_player_info(player_list)


# %% Matches
stats = spl.fetch_match_info('PlusLiga', 2022, 1102401)
stats
