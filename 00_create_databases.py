#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib
import sqlalchemy as sql

dbt = importlib.import_module('dbtools')
# importlib.reload(dbt)


# %% Common, predefined columns
db = dbt.get_engine('polish')
meta = sql.MetaData()

cols = {'league': sql.Column('League', sql.String, primary_key=True),
        'season': sql.Column('Season', sql.Integer, primary_key=True),
        'player': sql.Column('PlayerID', sql.Integer, primary_key=True),
        'team': sql.Column('TeamID', sql.Integer, primary_key=True),
        'match': sql.Column('MatchID', sql.Integer, primary_key=True)}


# %% Define lists
players_list = sql.Table(
    'players_list', meta,
    cols['league'],
    cols['season'],
    cols['player'],
    extend_existing=True)

teams_list = sql.Table(
    'teams_list', meta,
    cols['league'],
    cols['season'],
    cols['team'],
    extend_existing=True)

matches_list = sql.Table(
    'matches_list', meta,
    cols['league'],
    cols['season'],
    cols['match'],
    extend_existing=True)


# %% Define player tables
players_info = sql.Table(
    'players_info', meta,
    cols['league'],
    cols['season'],
    cols['player'],
    sql.Column('PlayerName', sql.String, nullable=False),
    sql.Column('TeamID', sql.Integer, nullable=False),
    sql.Column('DateOfBirth', sql.DateTime),
    sql.Column('Position', sql.String, nullable=False),
    sql.Column('Height', sql.Integer),
    sql.Column('Weight', sql.Integer),
    sql.Column('Reach', sql.Integer),
    extend_existing=True)


# %% Define team tables
teams_info = sql.Table(
    'teams_info', meta,
    cols['league'],
    cols['season'],
    cols['team'],
    sql.Column('TeamName', sql.String, nullable=False),
    extend_existing=True)

teams_roster = sql.Table(
    'teams_roster', meta,
    cols['league'],
    cols['season'],
    cols['team'],
    cols['player'],
    extend_existing=True)


# %% Define match tables
matches_info = sql.Table(
    'matches_info', meta,
    cols['league'],
    cols['season'],
    cols['match'],
    sql.Column('Home', sql.Integer, nullable=False),
    sql.Column('Away', sql.Integer, nullable=False),
    sql.Column('Date', sql.DateTime, nullable=False),
    sql.Column('Stage', sql.String),
    sql.Column('Round', sql.Integer),
    sql.Column('MatchNumber', sql.String),
    sql.Column('MVP', sql.Integer),
    sql.Column('Spectators', sql.Integer),
    sql.Column('FirstReferee', sql.String),
    sql.Column('SecondReferee', sql.String),
    sql.Column('Comissioner', sql.String),
    sql.Column('Arena', sql.String),
    sql.Column('Address', sql.String),
    sql.Column('City', sql.String),
    sql.Column('ArenaSize', sql.Integer),
    extend_existing=True)

matches_stats = sql.Table(
    'matches_stats', meta,
    cols['league'],
    cols['season'],
    cols['match'],
    cols['player'],
    sql.Column('SetI', sql.String),
    sql.Column('SetII', sql.String),
    sql.Column('SetIII', sql.String),
    sql.Column('SetIV', sql.String),
    sql.Column('SetV', sql.String),
    sql.Column('SetGolden', sql.String),
    sql.Column('Points', sql.Integer),
    sql.Column('BreakPoints', sql.Integer),
    sql.Column('PointsRatio', sql.Integer),
    sql.Column('ServeTotal', sql.Integer),
    sql.Column('ServeErrors', sql.Integer),
    sql.Column('ServeAces', sql.Integer),
    sql.Column('ServeSlashes', sql.Integer),
    sql.Column('ReceptionTotal', sql.Integer),
    sql.Column('ReceptionErrors', sql.Integer),
    sql.Column('ReceptionPositive', sql.Integer),
    sql.Column('ReceptionPerfect', sql.Intger),
    sql.Column('AttackTotal', sql.Integer),
    sql.Column('AttackBlocked', sql.Integer),
    sql.Column('AttackErrors', sql.Integer),
    sql.Column('AttackKills', sql.Integer),
    sql.Column('BlockPoints', sql.Integer),
    sql.Column('BlockAssists', sql.Integer),
    extend_existing=True)


# %% Create tables
meta.create_all(db)
