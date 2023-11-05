#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import pandas as pd
import datetime as dttm
import hashlib

def get_config():
    with open('config.json', 'r') as read_file:
        config = json.load(read_file)

    return config


def df_colattach1(df1, tab):
    n = df1.shape[0]
    if n != 1:
        raise ValueError(df1)

    df = df1.loc[df1.index.repeat(len(tab))].reset_index(drop=True)
    rslt = pd.concat([df, tab], axis=1)
    return rslt


def add_timestamp(tab):
    stamp = dttm.datetime.today()
    tab.insert(loc=tab.shape[1],
               column='Timestamp',
               value=stamp)


def create_hash(values):
    strings = list(str(x) for x in values)
    one_string = ' '.join(strings)
    enc_string = one_string.encode()
    rslt = hashlib.md5(enc_string).hexdigest()
    return rslt


def add_hash(tab):
    hashes = tab.apply(create_hash, axis=1)
    tab.insert(loc=tab.shape[1],
               column='Hash',
               value=hashes)
