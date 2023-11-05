#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib
import sqlalchemy as sql

dbt = importlib.import_module('dbtools')
# importlib.reload(dbt)


# %% Database objects
db = dbt.get_engine('polish', clean=True)
meta = sql.MetaData()


# %% Define lists
p_list = sql.Table(
    'players_list', meta,
    sql.Column('League', sql.String, primary_key=True),
    sql.Column('Season', sql.Integer, primary_key=True),
    sql.Column('PlayerID', sql.Integer, primary_key=True),
    sql.Column('Timestamp', sql.DateTime, nullable=False),
    extend_existing=True)

t_list = sql.Table(
    'teams_list', meta,
    sql.Column('League', sql.String, primary_key=True),
    sql.Column('Season', sql.Integer, primary_key=True),
    sql.Column('TeamID', sql.Integer, primary_key=True),
    sql.Column('Timestamp', sql.DateTime, nullable=False),
    extend_existing=True)

m_list = sql.Table(
    'matches_list', meta,
    sql.Column('League', sql.String, primary_key=True),
    sql.Column('Season', sql.Integer, primary_key=True),
    sql.Column('MatchID', sql.Integer, primary_key=True),
    sql.Column('Timestamp', sql.DateTime, nullable=False),
    extend_existing=True)


# %% Define player tables
p_info = sql.Table(
    'players_info', meta,
    sql.Column('League', sql.String, primary_key=True),
    sql.Column('Season', sql.Integer, primary_key=True),
    sql.Column('PlayerID', sql.Integer, primary_key=True),
    sql.Column('PlayerName', sql.String, nullable=False),
    sql.Column('TeamID', sql.Integer, nullable=False),
    sql.Column('DateOfBirth', sql.DateTime),
    sql.Column('Position', sql.String),
    sql.Column('Height', sql.Integer),
    sql.Column('Weight', sql.Integer),
    sql.Column('Reach', sql.Integer),
    sql.Column('Timestamp', sql.DateTime, nullable=False),
    extend_existing=True)


# %% Define team tables
t_info = sql.Table(
    'teams_info', meta,
    sql.Column('League', sql.String, primary_key=True),
    sql.Column('Season', sql.Integer, primary_key=True),
    sql.Column('TeamID', sql.Integer, primary_key=True),
    sql.Column('TeamName', sql.String, nullable=False),
    sql.Column('Timestamp', sql.DateTime, nullable=False),
    extend_existing=True)

t_roster = sql.Table(
    'teams_roster', meta,
    sql.Column('League', sql.String, primary_key=True),
    sql.Column('Season', sql.Integer, primary_key=True),
    sql.Column('TeamID', sql.Integer, primary_key=True),
    sql.Column('PlayerID', sql.Integer, primary_key=True),
    sql.Column('Timestamp', sql.DateTime, nullable=False),
    extend_existing=True)


# %% Define match tables
m_info = sql.Table(
    'matches_info', meta,
    sql.Column('League', sql.String, primary_key=True),
    sql.Column('Season', sql.Integer, primary_key=True),
    sql.Column('MatchID', sql.Integer, primary_key=True),
    sql.Column('Home', sql.Integer, nullable=False),
    sql.Column('Away', sql.Integer, nullable=False),
    sql.Column('Date', sql.DateTime),
    sql.Column('Stage', sql.String),
    sql.Column('Round', sql.Integer),
    sql.Column('MatchNumber', sql.String),
    sql.Column('MVP', sql.Integer),
    sql.Column('Spectators', sql.Integer),
    sql.Column('FirstReferee', sql.String),
    sql.Column('SecondReferee', sql.String),
    sql.Column('Commissioner', sql.String),
    sql.Column('InspectorReferee', sql.String),
    sql.Column('Arena', sql.String),
    sql.Column('Address', sql.String),
    sql.Column('City', sql.String),
    sql.Column('ArenaSize', sql.Integer),
    sql.Column('Timestamp', sql.DateTime, nullable=False),
    extend_existing=True)

m_stats = sql.Table(
    'matches_stats', meta,
    sql.Column('League', sql.String, primary_key=True),
    sql.Column('Season', sql.Integer, primary_key=True),
    sql.Column('MatchID', sql.Integer, primary_key=True),
    sql.Column('PlayerID', sql.Integer, primary_key=True),
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
    sql.Column('ReceptionNegative', sql.Integer),
    sql.Column('ReceptionPositive', sql.Integer),
    sql.Column('ReceptionPerfect', sql.Integer),
    sql.Column('AttackTotal', sql.Integer),
    sql.Column('AttackBlocked', sql.Integer),
    sql.Column('AttackErrors', sql.Integer),
    sql.Column('AttackKills', sql.Integer),
    sql.Column('BlockPoints', sql.Integer),
    sql.Column('BlockAssists', sql.Integer),
    sql.Column('Timestamp', sql.DateTime, nullable=False),
    extend_existing=True)

m_results = sql.Table(
    'matches_results', meta,
    sql.Column('League', sql.String, primary_key=True),
    sql.Column('Season', sql.Integer, primary_key=True),
    sql.Column('MatchID', sql.Integer, primary_key=True),
    sql.Column('Set', sql.Integer, primary_key=True),
    sql.Column('Time', sql.String),
    sql.Column('Points', sql.String),
    sql.Column('Result', sql.String),
    sql.Column('Timestamp', sql.DateTime, nullable=False),
    extend_existing=True)


# %% Create tables
meta.create_all(db)
