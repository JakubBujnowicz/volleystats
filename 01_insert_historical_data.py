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


# %% Getting all combinations for which the data should be fetched
combs = dict()
for league in config['leagues']['polish']:
    seasons = np.arange(start=config['first_season'][league],
                        stop=spl.current_season())
    curr = pd.DataFrame(dict(Season=seasons))
    curr.insert(loc=0, column='League', value=league)
    combs[league] = curr

combs = pd.concat(combs, ignore_index=True)


# %% Fetch and upload data
for i in range(len(combs.index)):
    league = combs.League[i]
    season = combs.Season[i]

    print('Fetching data for {league}: {start}/{end}...'.format(
        league=league,
        start=season,
        end=season + 1))

    tabs = dict()
    tabs['matches_list'] = spl.fetch_matches(league, season)
    matches_data = spl.batch_fetch_match_info(tabs['matches_list'])
    tabs['matches_info'] = matches_data['information']
    tabs['matches_stats'] = matches_data['stats']
    tabs['matches_results'] = matches_data['results']

    tabs['teams_list'] = spl.fetch_teams(league, season)
    teams_data = spl.batch_fetch_team_info(tabs['teams_list'])
    tabs['teams_info'] = teams_data['information']
    tabs['teams_roster'] = teams_data['roster']

    tabs['players_list'] = spl.fetch_players(league, season)
    # Since players come and go, the full players list should be extended
    # by all players from statistics
    plist_stats = tabs['matches_stats'][['League', 'Season', 'PlayerID']]
    tabs['players_list'] = pd.concat([tabs['players_list'], plist_stats],
                                     ignore_index=True).drop_duplicates()
    tabs['players_list'] = tabs['players_list'].reset_index(drop=True)

    # Some matches with unnamed players in Stats pop-up
    # PlayerID = 0 crashes players_info, as it redirects to all players list
    tabs['players_list'] = tabs['players_list'].query('PlayerID > 0')

    tabs['players_info'] = spl.batch_fetch_player_info(tabs['players_list'])

    for tab in tabs.keys():
        vsu.add_timestamp(tabs[tab])


    # %% Inserting into database
    for tab in tabs.keys():
        tabs[tab].to_sql(name=tab,
                         con=db,
                         index=False,
                         if_exists='append')
        # db.connect().execute(sql.text('SELECT * FROM ' + tab)).fetchall()
