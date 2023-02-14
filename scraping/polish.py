#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lxml import html
import requests
import re
import numpy as np
import pandas as pd


# %% Tools
def url_league(league, *args):
    """
    Creates a basic URL for a given league
    """

    sites = {'PlusLiga': 'https://www.plusliga.pl',
             'Tauron Liga': 'https://www.tauronliga.pl',
             'Tauron 1. Liga': 'https://tauron1liga.pl'}
    rslt = [sites[league], *args]
    rslt = '/'.join(str(x) for x in rslt) + '.html'
    return rslt


def extract_ids(strings):
    """
    Extracts Player/Team IDs from URLs
    """

    expr = re.compile('(?<=id/)[0-9]+')
    rslt = np.array(list(expr.findall(s)[0] for s in strings),
                    dtype=np.int64)
    return rslt


def translate_positions(strings):
    """
    Converts Polish position names into english equivalents.
    """

    # TODO: Replace male positions into universal using regex
    # The acronyms to be decided, it seems that there is no universally
    # accepted terminology
    pl2en = {'przyjmujący': 'OH',
             'atakujący': 'RSH',
             'środkowy': 'MBH',
             'libero': 'Libero',
             'rozgrywający': 'Setter'}

    # Lower used due to website's inconsistency
    rslt = [pl2en[i.lower()] for i in strings]
    return rslt


def perc2count(perc, total):
    perc = pd.Series(list(x[:-1] for x in perc))
    perc[perc == ''] = 0
    perc = np.array(perc, dtype=np.float64) / 100

    rslt = np.round(perc * total).astype(np.int32)
    return rslt


# %% Players
def fetch_players(league, season):
    """
    Scraps a player list for a given league and season.
    Lower level function for a single combination of those factors,
    accesses a corresponding website once.
    """

    url = url_league(league, 'players/tour', season)
    req = requests.get(url)
    content = req.content
    tree = html.fromstring(content)

    links = tree.cssselect('div.caption > h3 > a')
    ids = extract_ids(list(x.get('href') for x in links))

    rslt = pd.DataFrame({'League': league,
                         'Season': season,
                         'PlayerID': ids})
    rslt.Season = rslt.Season.astype(np.int32)
    return rslt


def fetch_player_info(league, season, ID):
    """
    Scraps information about a player with a given league, ID and season.
    Lower level function for a single combination of those factors,
    accesses a corresponding website once.
    """
    # NOTE: I'd prefer ID to be lowercase, however that is already a Python
    # function, maybe consider some other naming or keep it as it is

    info = [league, season, ID]
    url = url_league(league, 'players/tour', season, 'id', ID)

    # Website redirects links for seasons a player did not take part in
    # to the newest season -- checked and empty list returned here
    req = requests.get(url)
    if req.url != url:
        return []

    content = req.content
    tree = html.fromstring(content)
    selector = ' > '.join(['div.pagecontent:nth-child(1)',
                           'div:nth-child(1)',
                           'div:nth-child(1) span'])
    metrics = tree.cssselect(selector)
    team = tree.cssselect('.playerteamname > a:nth-child(1)')
    name = tree.cssselect('.playername')[0].text

    metrics = list(i.text.strip() for i in metrics)
    metrics[0] = team[0].get('href')

    # Sometimes data is unavailable (especially Reach for liberos),
    # empty string crashes later functions
    # TODO: There must be a better, more robust way to do this
    for index, value in enumerate(metrics):
        if value == '':
            metrics[index] = None

    info.append(name)
    info.extend(metrics)

    # TODO: Player's team history table is available under the same URL,
    # it should be considered to add it here
    # pd.read_html(content)

    return info


def batch_fetch_player_info(combinations):
    """
    Runs a lower level function for all combinations and prepares a pd.DataFrame
    with correct data formatting.
    """
    # TODO: The interface should be reviewed here, simply a draft below
    # Maybe it can be done a little bit smarter
    rslt = list(fetch_player_info(*x) for x in combinations.values)

    rslt = pd.DataFrame(rslt, columns=['League', 'Season', 'PlayerID',
                                       'PlayerName', 'TeamID', 'DateOfBirth',
                                       'Position', 'Height', 'Weight', 'Reach'])
    rslt.dropna(axis=0, how='all', inplace=True)

    # NOTE: Should setting correct types be here or in a lower level function?
    # Perhaps it's more efficient to do it here, while the other way would
    # be more versatile
    rslt = rslt.astype({'Season': np.int32,
                        'PlayerID': np.in64,
                        'Height': np.int32,
                        'Weight': np.int32,
                        'Reach': np.int32})
    rslt.TeamID = extract_ids(rslt.TeamID)
    rslt.DateOfBirth = pd.to_datetime(rslt.DateOfBirth, format='%d.%m.%Y')
    rslt.Position = translate_positions(rslt.Position)
    return rslt


# %% Teams
def fetch_teams(league, season):
    """
    Scraps a teams list for a given league and season.
    Lower level function for a single combination of those factors,
    accesses a corresponding website once.
    """

    url = url_league(league, 'teams/tour', season)
    req = requests.get(url)
    content = req.content
    tree = html.fromstring(content)

    links = tree.cssselect('div.thumbnail.teamlist > a')
    ids = extract_ids(list(x.get('href') for x in links))

    rslt = pd.DataFrame({'League': league,
                         'Season': season,
                         'TeamID': ids})
    rslt.Season = rslt.Season.astype(np.int32)
    return rslt


def fetch_team_info(league, season, ID):
    url = url_league(league, 'teams/id', ID, 'tour', season)
    # TODO: Finish, consider what should be returned (name, roster, something else?)
    pass


# %% Standings
def fetch_standings(league, season):
    url = url_league(league, 'table/tour', season)
    ## TODO: Finish
    pass


# %% Matches
def fetch_matches(league, season):
    """
    Scraps a matches list for a given league and season.
    Lower level function for a single combination of those factors,
    accesses a corresponding website once.
    """

    url = url_league(league, 'games/tour', season)
    req = requests.get(url)
    content = req.content
    tree = html.fromstring(content)

    links = tree.cssselect('div.gameresult.clickable')
    ids = extract_ids(list(x.get('onclick') for x in links))

    rslt = pd.DataFrame({'League': league,
                         'Season': season,
                         'MatchID': ids})
    rslt.Season = rslt.Season.astype(np.int32)
    return rslt


def parse_stats_table(tab):
    player_ids = list(a.get('href')
                      for a in tab.cssselect('th.min-responsive > a'))

    rows = tab.cssselect('tr')
    values = list(list(val.text for val in rows[i].cssselect('td'))
                  for i in range(len(rows) - 1))  # Last row is skipped as it is a total
    rslt = pd.DataFrame(values,
                        columns=['SetI', 'SetII', 'SetIII', 'SetIV', 'SetV',
                                 'Points', 'BreakPoints', 'PointsRatio',
                                 'ServeTotal', 'ServeErrors', 'ServeAces', 'ServeEff',
                                 'ReceptionTotal', 'ReceptionErrors',
                                 'ReceptionPosPerc', 'ReceptionPerfPerc',
                                 'AttackTotal', 'AttackBlocked', 'AttackErrors',
                                 'AttackKills', 'AttackKillPerc', 'AttackEff',
                                 'BlockPoints', 'BlockAssists'])
    rslt.insert(loc=0, column='PlayerID', value=player_ids)

    return rslt


def fetch_match_info(league, season, ID):
    # TODO: Finish, consider what should be returned (teams, result, time,
    # place, something else?)

    url = url_league(league, 'games/id', ID, 'tour', season)

    req = requests.get(url)
    content = req.content
    tree = html.fromstring(content)

    # Statistics --------------------------------------------------------------
    stat_tabs = tree.cssselect('table.rs-standings-table > tbody')

    stats = pd.concat(list(parse_stats_table(tab) for tab in stat_tabs))
    stats.reset_index(drop=True, inplace=True)
    stats.insert(loc=0,
                 column='MatchID',
                 value=ID)

    # Change column types
    stats = stats.astype({'MatchID': np.int64,
                          'Points': np.int32,
                          'BreakPoints': np.int32,
                          'PointsRatio': np.int32,
                          'ServeTotal': np.int32,
                          'ServeErrors': np.int32,
                          'ServeAces': np.int32,
                          'ReceptionTotal': np.int32,
                          'ReceptionErrors': np.int32,
                          'AttackTotal': np.int32,
                          'AttackBlocked': np.int32,
                          'AttackErrors': np.int32,
                          'AttackKills': np.int32,
                          'BlockPoints': np.int32,
                          'BlockAssists': np.int32})
    stats.PlayerID = extract_ids(stats.PlayerID)
    stats.insert(loc=int(np.argmax(stats.columns == 'ServeEff')),
                  column='ServeSlashes',
                  value=perc2count(perc=stats.ServeEff, total=stats.ServeTotal) -
                      stats.ServeAces + stats.ServeErrors)
    stats.insert(loc=int(np.argmax(stats.columns == 'ReceptionPosPerc')),
                  column='ReceptionPositive',
                  value=perc2count(perc=stats.ReceptionPosPerc,
                                   total=stats.ReceptionTotal))
    stats.insert(loc=int(np.argmax(stats.columns == 'ReceptionPerfPerc')),
                  column='ReceptionPerfect',
                  value=perc2count(perc=stats.ReceptionPerfPerc,
                                   total=stats.ReceptionTotal))

    # Drop unnecessary columns (functions of other variables)
    stats.drop(columns=['ServeEff', 'ReceptionPosPerc', 'ReceptionPerfPerc',
                        'AttackKillPerc', 'AttackEff'],
               inplace=True)

    return stats
