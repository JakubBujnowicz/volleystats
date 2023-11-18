#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

    tabs = spl.fetch_all(league, season)

    for tab in tabs.keys():
        vsu.add_hash(tabs[tab])
        vsu.add_timestamp(tabs[tab])


    # %% Inserting into database
    for tab in tabs.keys():
        rows_aff = tabs[tab].to_sql(name=tab,
                                    con=db,
                                    index=False,
                                    if_exists='append')
        print("Inserted {n} rows into '{tab}'...".format(
              n=rows_aff,
              tab=tab))
        # db.connect().execute(sql.text('SELECT * FROM ' + tab)).fetchall()
