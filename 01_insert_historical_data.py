#!/usr/bin/env python3
# -*- coding: utf-8 -*-

## TODO: To be split into two codes: one inserting historical data and second
## inserting data from the current season. At the moment only current season
## is taken into account.

import importlib
import sqlalchemy as sql
import pandas as pd
import numpy as np

vsu = importlib.import_module('vsutils')
# importlib.reload(vsu)
spl = importlib.import_module('scraping.polish')
# importlib.reload(spl)
dbt = importlib.import_module('dbtools')
# importlib.reload(dbt)


# %% Get config and database engine
config = vsu.get_config()
db = dbt.get_engine('polish')


# %% Fetching
league = config['leagues']['polish'][0]
season = 2022

players_list = spl.fetch_players(league, season)
players_info = spl.batch_fetch_player_info(players_list)

teams_list = spl.fetch_teams(league, season)
teams_data = spl.batch_fetch_team_info(teams_list)
teams_info = teams_data['information']
teams_roster = teams_data['roster']

matches_list = spl.fetch_matches(league, season)
matches_data = spl.batch_fetch_match_info(matches_list)
matches_info = matches_data['information']
matches_stats = matches_data['stats']
matches_results = matches_data['results']


# %% Inserting into database
players_list.to_sql(name='players_list',
                    con=db,
                    index=False,
                    if_exists='append')
# db.connect().execute('SELECT * FROM players_list').fetchall()

players_info.to_sql(name='players_info',
                    con=db,
                    index=False,
                    if_exists='append')
# db.connect().execute('SELECT * FROM players_info').fetchall()

teams_list.to_sql(name='teams_list',
                  con=db,
                  index=False,
                  if_exists='append')
# db.connect().execute('SELECT * FROM teams_list').fetchall()

teams_info.to_sql(name='teams_info',
                  con=db,
                  index=False,
                  if_exists='append')
# db.connect().execute('SELECT * FROM teams_info').fetchall()

teams_roster.to_sql(name='teams_roster',
                    con=db,
                    index=False,
                    if_exists='append')
# db.connect().execute('SELECT * FROM teams_roster').fetchall()

matches_list.to_sql(name='matches_list',
                    con=db,
                    index=False,
                    if_exists='append')
# db.connect().execute('SELECT * FROM matches_list').fetchall()

matches_info.to_sql(name='matches_info',
                    con=db,
                    index=False,
                    if_exists='append')
# db.connect().execute('SELECT * FROM matches_info').fetchall()

matches_stats.to_sql(name='matches_stats',
                     con=db,
                     index=False,
                     if_exists='append')
# db.connect().execute('SELECT * FROM matches_stats').fetchall()

matches_results.to_sql(name='matches_results',
                       con=db,
                       index=False,
                       if_exists='append')
# db.connect().execute('SELECT * FROM matches_results').fetchall()
