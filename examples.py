#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib
import itertools
import pandas as pd

spl = importlib.import_module('scraping.polish')
importlib.reload(spl)

lg = ['PlusLiga']
ids = [30339, 448, 27975]
sns = list(range(2015, 2022))
combs = pd.DataFrame(itertools.product(lg, sns, ids))

spl.fetch_player_info('PlusLiga', 2022, 30339)

info = spl.prepare_player_info(combs)
info
