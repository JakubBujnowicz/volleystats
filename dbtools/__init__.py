#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlalchemy as sql
import vsutils as vsu

def get_engine(db_name, echo=True):
    config = vsu.get_config()

    db_path = 'sqlite+pysqlite:///{dir}/{name}'.format(
        dir=config['paths']['data_dir'],
        name=config['paths']['db_names'][db_name])
    engine = sql.create_engine(db_path, echo=echo)

    return engine
