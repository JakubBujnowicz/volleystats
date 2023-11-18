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
season = spl.current_season()


# %% Fetch and upload data
for league in config['leagues']['polish']:
    print('Fetching data for {league}: {start}/{end}...'.format(
        league=league,
        start=season,
        end=season + 1))

    tabs = spl.fetch_all(league, season)

    for tab in tabs.keys():
        vsu.add_hash(tabs[tab])
        vsu.add_timestamp(tabs[tab])


    # %% Inserting into database
    hash_query = """SELECT DISTINCT Hash
    FROM {tab}
    WHERE Season = {season}
        AND League = '{league}'"""

    db_con = db.connect()
    for tab in tabs.keys():
        curr_query = hash_query.format(tab=tab, season=season, league=league)
        curr_hashes = db_con.execute(sql.text(curr_query)).fetchall()
        curr_hashes = set(x[0] for x in curr_hashes)

        ins_tab = tabs[tab]
        ins_tab = ins_tab[~ins_tab.Hash.isin(curr_hashes)]

        if ins_tab.shape[0] > 0:
            rows_aff = ins_tab.to_sql(name=tab,
                                      con=db,
                                      index=False,
                                      if_exists='append')
            print("Inserted {n} rows into '{tab}'...".format(
                n=rows_aff,
                tab=tab))
            # db.connect().execute(sql.text('SELECT * FROM ' + tab)).fetchall()
