#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlalchemy as sql
import vsutils as vsu
import os

def get_db_path(db_name):
    config = vsu.get_config()

    db_path = '{dir}/{name}'.format(
        dir=config['paths']['data_dir'],
        name=config['paths']['db_names'][db_name])
    return db_path

def get_engine(db_name, echo=True, clean=False):
    db_path = get_db_path(db_name)
    sqlite_path = 'sqlite+pysqlite:///' + db_path

    if clean and os.path.exists(db_path):
        os.remove(db_path)

    engine = sql.create_engine(sqlite_path, echo=echo)
    return engine
