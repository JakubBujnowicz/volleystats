#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import pandas as pd


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
