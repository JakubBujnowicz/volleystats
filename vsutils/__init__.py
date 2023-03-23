#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

def df_colattach1(df1, tab):
    n = df1.shape[0]
    if n != 1:
        raise ValueError(df1)

    df = df1.loc[df1.index.repeat(len(tab))].reset_index(drop=True)
    rslt = pd.concat([df, tab], axis=1)
    return rslt
