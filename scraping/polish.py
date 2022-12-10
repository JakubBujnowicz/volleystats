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
                    dtype=np.int32)
    return rslt


def translate_positions(strings):
    """
    Converts Polish position names into english equivalents.
    """

    ## TODO: Replace male positions into universal using regex
    ## TODO: Complete the libero/setter positions
    # The acronyms to be decided, it seems that there is no universally
    # accepted terminology
    pl2en = {'przyjmujący': 'OH',
             'atakujący': 'RSH',
             'środkowy': 'MBH'}

    # Lower used due to website's inconsistency
    rslt = [pl2en[i.lower()] for i in strings]
    return rslt


# %% Players
def fetch_players(league, season):
    url = url_league(league, 'players/tour', season)
    ## TODO: Finish, should contain IDs of all players
    pass


def fetch_player_info(league, season, ID):
    """
    Scraps information about a player with a given league, ID and season.
    Lower level function for a single combination of those factors,
    accesses a corresponding website once.
    """
    ## NOTE: I'd prefer ID to be lowercase, however that is already a Python
    ## function, maybe consider some other naming or keep it as it is

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

    info.append(name)
    info.extend(metrics)

    ## TODO: Player's team history table is available under the same URL,
    ## it should be considered to add it here
    # pd.read_html(content)

    return info


def prepare_player_info(combinations):
    """
    Runs a lower level function for all combinations and prepares a pd.DataFrame
    with correct data formatting.
    """
    ## TODO: The interface should be reviewed here, simply a draft below
    ## Maybe it can be done a little bit smarter
    rslt = list(fetch_player_info(*x) for x in combinations.values)

    rslt = pd.DataFrame(rslt, columns=['League', 'Season', 'PlayerID',
                                       'PlayerName', 'TeamID', 'DateOfBirth',
                                       'Position', 'Height', 'Weight', 'Reach'])
    rslt.dropna(axis=0, how='all', inplace=True)

    rslt.Season = rslt.Season.astype('Int32')
    rslt.PlayerID = rslt.PlayerID.astype('Int64')
    rslt.TeamID = extract_ids(rslt.TeamID)
    rslt.DateOfBirth = pd.to_datetime(rslt.DateOfBirth, format = '%d.%m.%Y')
    rslt.Position = translate_positions(rslt.Position)
    rslt.Height = rslt.Height.astype('Int32')
    rslt.Weight = rslt.Weight.astype('Int32')
    rslt.Reach = rslt.Reach.astype('Int32')
    return rslt


# %% Teams
def fetch_teams(league, season):
    url = url_league(league, 'teams/tour', season)
    ## TODO: Finish, should contain IDs of all teams
    pass


def fetch_team_info(league, season, ID):
    url = url_league(league, 'teams/id', ID, 'tour', season)
    ## TODO: Finish, consider what should be returned (name, squad, something else?)
    pass


# %% Standings
def fetch_standings(league, season):
    url = url_league(league, 'table/tour', season)
    ## TODO: Finish
    pass


# %% Matches
def fetch_matches(league, season):
    url = url_league(league, 'games/tour', season)
    ## TODO: Finish, should contain IDs of all matches
    pass


def fetch_match_info(league, season, ID):
    url = url_league(league, 'games/id', ID, 'tour', season)
    ## TODO: Finish, consider what should be returned (teams, result, time,
    ## place, stats, something else?)
    pass
