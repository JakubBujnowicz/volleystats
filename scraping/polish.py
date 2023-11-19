#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lxml import html
import requests
import re
import numpy as np
import pandas as pd
import vsutils as vsu
from datetime import datetime, date


# %% Tools
def url_league(league, *args):
    """
    Creates a basic URL for a given league
    """

    sites = {'PlusLiga': 'https://www.plusliga.pl',
             'Tauron Liga': 'https://www.tauronliga.pl',
             'Tauron 1. Liga': 'https://www.tauron1liga.pl'}
    rslt = [sites[league], *args]
    rslt = '/'.join(str(x) for x in rslt) + '.html'
    return rslt


def make_request(url):
    """
    Makes a request with a proper encoding.
    """

    req = requests.get(url)
    req.encoding = 'Latin-2'
    return req


def extract_ids(strings):
    """
    Extracts Player/Team IDs from URLs
    """

    expr = re.compile('(?<=id/)[0-9]+')

    rslt = list()
    for s in strings:
        rslt.extend(expr.findall(s))

    rslt = np.array(rslt, dtype=np.int64)
    return rslt


def translate_positions(strings):
    """
    Converts Polish position names into English equivalents.
    """

    # Last letter removed to avoid gender issues
    pl2en = {'przyjmując': 'OH',
             'atakując': 'RSH',
             'środkow': 'MBH',
             'liber': 'Libero',
             'rozgrywając': 'Setter'}
    # TODO: The acronyms to be decided, it seems that there is no universally
    # accepted terminology

    rslt = list()
    for string in strings:
        if string is None:
            rslt.append(None)
        else:
            # Lower used due to website's inconsis0tency
            rslt.append(pl2en[string[:-1].lower()])

    return rslt


def translate_terms(strings):
    """
    Converts Polish terms into English equivalents.
    """

    pl2en = {'Faza': 'Stage',
             'Termin': 'Round',
             'Numer meczu': 'MatchNumber',
             'MVP': 'MVP',
             'Liczba widzów': 'Spectators',
             'Sędzia pierwszy': 'FirstReferee',
             'Sędzia drugi': 'SecondReferee',
             # TODO: Other translation should be considered
             'Kwalifikator': 'InspectorReferee',
             'Komisarz': 'Commissioner',
             'Nazwa': 'Arena',
             'Adres': 'Address',
             'Miasto': 'City',
             'Liczba miejsc siedzących w hali': 'ArenaSize',
             'zasadnicza': 'main'}

    if isinstance(strings, list):
        rslt = list(pl2en[i] for i in strings)
    elif isinstance(strings, pd.core.series.Series):
        rslt = strings.replace(pl2en)

    return rslt


def perc2count(perc, total):
    """
    Infers an integer value from total * perc / 100.
    """

    perc = pd.Series(list(x[:-1] for x in perc))
    perc[perc == ''] = 0
    perc = np.array(perc, dtype=np.float64) / 100

    rslt = np.round(perc * total).astype(np.int32)
    return rslt


def current_season(cutoff = 7):
    """
    Infers current season (starting year, integer). Cutoff determines how long
    a season runs into the next year, where it should be counted as starting
    in the previous one (e.g. for cutoff of 7, the May of 2023 is counted
    as season 2022/2023, hence 2022 should be returned).
    """

    today = date.today()
    rslt = today.year
    if today.month <= cutoff:
        rslt -= 1

    return rslt


# %% Players
def fetch_players(league, season):
    """
    Scraps a player list for a given league and season.
    Lower level function for a single combination of those factors,
    accesses a corresponding website once.
    """

    url = url_league(league, 'players/tour', season)
    req = make_request(url)
    tree = html.fromstring(req.text)

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

    # Sometimes a player's info page is broken, happens to Alan Sket (2100352)
    # Results in too many redirects, return without info in this case
    try:
        req = make_request(url)
    except:
        return []

    # Website redirects links for seasons a player did not take part in
    # to the newest season -- checked and empty list returned here
    if req.url != url:
        return []

    tree = html.fromstring(req.text)
    selector = ' > '.join(['div.pagecontent:nth-child(1)',
                           'div:nth-child(1)',
                           'div:nth-child(1) span'])
    metrics = tree.cssselect(selector)
    team = tree.cssselect('.playerteamname > a:nth-child(1)')
    name = tree.cssselect('.playername')[0].text

    metrics = list(i.text for i in metrics)
    for i in range(len(metrics)):
        if metrics[i] is not None:
            metrics[i] = metrics[i].strip()

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
    combinations = combinations.loc[:, ['League', 'Season', 'PlayerID']]
    rslt = list(fetch_player_info(*x) for x in combinations.values)

    rslt = pd.DataFrame(rslt, columns=['League', 'Season', 'PlayerID',
                                       'PlayerName', 'TeamID', 'DateOfBirth',
                                       'Position', 'Height', 'Weight', 'Reach'])
    rslt.dropna(axis=0, how='all', inplace=True)
    rslt.reset_index(drop=True, inplace=True)

    # NOTE: Should setting correct types be here or in a lower level function?
    # Perhaps it's more efficient to do it here, while the other way would
    # be more versatile
    rslt = rslt.astype({'Season': np.int32,
                        'PlayerID': np.int64,
                        ## TODO: Floats below due to possible missings,
                        ## perhaps this could be improved
                        'Height': np.float32,
                        'Weight': np.float32,
                        'Reach': np.float32})
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
    req = make_request(url)
    tree = html.fromstring(req.text)

    links = tree.cssselect('div.thumbnail.teamlist > a')
    ids = extract_ids(list(x.get('href') for x in links))

    rslt = pd.DataFrame({'League': league,
                         'Season': season,
                         'TeamID': ids})
    rslt.Season = rslt.Season.astype(np.int32)
    return rslt


def _parse_teaminfo_table(tab):
    ## TODO: Finish, does not work at the moment
    pars = tab.cssselect('p')
    texts = list(''.join(par.itertext()) for par in pars)
    texts = list(re.split(pattern=r'[\n\t\r]+', string=txt) for txt in texts)

    return None


def fetch_team_info(league, season, ID):
    url = url_league(league, 'teams/id', ID, 'tour', season)
    # TODO: Finish, consider what should be returned (name, roster, something else?)

    req = make_request(url)
    tree = html.fromstring(req.text)

    ids = pd.DataFrame([{'League': league,
                         'Season': season,
                         'TeamID': ID}])
    ids = ids.astype({'Season': np.int32,
                      'TeamID': np.int64})

    # Roster ------------------------------------------------------------------
    players = tree.cssselect('div.player-item.to-filter.cut-paste > a')
    players = extract_ids(list(p.get('href') for p in players))
    players = pd.DataFrame(players, columns=['PlayerID'])
    players = vsu.df_colattach1(ids, players)


    # Information -------------------------------------------------------------
    ## TODO: Finish this
    info = tree.cssselect('div.col-sm-12 > div.pagecontent > div.row')[0]
    # info = _parse_teaminfo_table(info)

    team_name = tree.cssselect('div > h1')[0]
    info = ids.copy()
    info['TeamName'] = team_name.text

    # Return values -----------------------------------------------------------
    rslt = {'information': info,
            'roster': players}

    return rslt


def batch_fetch_team_info(combinations):
    """
    Runs a lower level function for all combinations and concatenates DataFrames.
    """
    # TODO: The interface should be reviewed here, simply a draft below
    # Maybe it can be done a little bit smarter
    combinations = combinations.loc[:, ['League', 'Season', 'TeamID']]
    data = list(fetch_team_info(*x) for x in combinations.values)

    rslt = dict()
    for key in data[0].keys():
       rslt[key] = pd.concat(list(x[key] for x in data),
                             ignore_index=True)

    return rslt


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
    req = make_request(url)
    tree = html.fromstring(req.text)

    links = tree.cssselect('div.gameresult.clickable')
    ids = extract_ids(list(x.get('onclick') for x in links))

    rslt = pd.DataFrame({'League': league,
                         'Season': season,
                         'MatchID': ids})
    rslt.Season = rslt.Season.astype(np.int32)

    # Dropping duplicated matches
    rslt = rslt.drop_duplicates()

    return rslt


def _parse_stats_table(tab, season):
    head = tab.cssselect('thead')[0]
    body = tab.cssselect('tbody')[0]

    # Get PlayerIDs
    player_ids = list(a.get('href')
                      for a in body.cssselect('th.min-responsive > a'))

    # Get header row with column names
    # Second row chosen, as first are pasted column names
    header_cols = head.cssselect('tr')[1]
    header_cols = list(row.text for row in header_cols.cssselect('th'))

    # Get contents of the table
    rows = body.cssselect('tr')
    values = list(list(val.text for val in rows[i].cssselect('td'))
                  for i in range(len(rows) - 1))  # Last row is skipped as it is a total

    # Prepare table headers
    set_cols = ['SetI', 'SetII', 'SetIII', 'SetIV', 'SetV']

    # Choose columns according to old or new format
    if season >= 2008 and season <= 2019:
        old_format = True
        other_cols = ['Points',
                      'ServeTotal', 'ServeAces', 'ServeErrors', 'AcesSet',
                      'ReceptionTotal', 'ReceptionErrors', 'ReceptionNegative',
                      'ReceptionPositive', 'ReceptionPosPerc',
                      'ReceptionPerfect', 'ReceptionPerfPerc',
                      'AttackTotal', 'AttackErrors', 'AttackBlocked',
                      'AttackKills', 'AttackKillPerc',
                      'BlockPoints', 'BlocksSet']

    elif season >= 2020:
        old_format = False
        other_cols = ['Points', 'BreakPoints', 'PointsRatio',
                      'ServeTotal', 'ServeErrors', 'ServeAces', 'ServeEff',
                      'ReceptionTotal', 'ReceptionErrors',
                      'ReceptionPosPerc', 'ReceptionPerfPerc',
                      'AttackTotal', 'AttackBlocked', 'AttackErrors',
                      'AttackKills', 'AttackKillPerc', 'AttackEff',
                      'BlockPoints', 'BlockAssists']

    else:
        return None

    # Adjust set_cols if golden set is included
    if 'GS' in header_cols:
        set_cols.append('SetGolden')

    # Final list of column names
    all_cols = set_cols + other_cols

    # Prepare a data frame
    rslt = pd.DataFrame(values,
                        columns=all_cols)
    rslt.insert(loc=0, column='PlayerID', value=player_ids)

    # Change column types
    rslt.PlayerID = extract_ids(rslt.PlayerID)
    rslt = rslt.astype({'Points': np.int32,
                        'ServeTotal': np.int32,
                        'ServeErrors': np.int32,
                        'ServeAces': np.int32,
                        'ReceptionTotal': np.int32,
                        'ReceptionErrors': np.int32,
                        'AttackTotal': np.int32,
                        'AttackBlocked': np.int32,
                        'AttackErrors': np.int32,
                        'AttackKills': np.int32,
                        'BlockPoints': np.int32})

    if old_format:
        rslt = rslt.astype({'ReceptionNegative': np.int32,
                            'ReceptionPositive': np.int32,
                            'ReceptionPerfect': np.int32})

        # Drop unnecessary columns (functions of other variables)
        rslt = rslt.drop(columns=['AcesSet', 'ReceptionPosPerc',
                                  'ReceptionPerfPerc', 'AttackKillPerc',
                                  'BlocksSet'])

    else:
        rslt = rslt.astype({'BreakPoints': np.int32,
                            'PointsRatio': np.int32,
                            'BlockAssists': np.int32})

        rslt.insert(loc=int(np.argmax(rslt.columns == 'ServeEff')),
                    column='ServeSlashes',
                    value=perc2count(perc=rslt.ServeEff,
                                     total=rslt.ServeTotal) -
                        rslt.ServeAces +
                        rslt.ServeErrors)
        rslt.insert(loc=int(np.argmax(rslt.columns == 'ReceptionPosPerc')),
                    column='ReceptionPositive',
                    value=perc2count(perc=rslt.ReceptionPosPerc,
                                     total=rslt.ReceptionTotal))
        rslt.insert(loc=int(np.argmax(rslt.columns == 'ReceptionPerfPerc')),
                    column='ReceptionPerfect',
                    value=perc2count(perc=rslt.ReceptionPerfPerc,
                                     total=rslt.ReceptionTotal))

        # Drop unnecessary columns (functions of other variables)
        rslt = rslt.drop(columns=['ServeEff', 'ReceptionPosPerc',
                                  'ReceptionPerfPerc',
                                  'AttackKillPerc', 'AttackEff'])

    return rslt


def _parse_details_table(tab):
    labels = tab.cssselect('td')
    labels = list(x.text[:-1] for x in labels if x.text is not None)
    labels = translate_terms(labels)

    values = tab.cssselect('td > span')
    values = list(x.text for x in values)

    rslt = dict(zip(labels, values))
    if 'MVP' in labels:
        rslt['MVP'] = extract_ids([tab.cssselect('a')[0].get('href')])

    rslt = pd.DataFrame([rslt])
    types = {'Round': np.int32,
             # 'MatchNumber': np.int32, (Matches are number using letters in playoffs)
             'MVP': np.int64,
             'Spectators': np.int32,
             'ArenaSize': pd.Int32Dtype()} # There are sometimes NAs in old data
    rslt = rslt.astype({k: v for k, v in types.items() if k in rslt.columns})

    if 'Stage' in rslt.columns:
        rslt.Stage = translate_terms(rslt.Stage)

    return rslt


def _parse_results_table(tab):
    rows = tab.cssselect('tr')

    # Discard first (headers) and last (total)
    rows = rows[1:(len(rows) - 1)]
    values = list([x.text for x in row] for row in rows)
    rslt = pd.DataFrame(values, columns=['Set', 'Time', 'Points', 'Result'])

    # Fix the set number
    n = rslt.shape[0]
    rslt.Set = np.arange(n) + 1

    return rslt


def fetch_match_info(league, season, ID):
    # TODO: Finish, consider what should be returned (teams, result, time,
    # place, something else?)
    url = url_league(league, 'games/id', ID, 'tour', season)

    req = make_request(url)
    tree = html.fromstring(req.text)

    ids = pd.DataFrame([{'League': league,
                         'Season': season,
                         'MatchID': ID}])
    ids = ids.astype({'Season': np.int32,
                      'MatchID': np.int64})

    # Information -------------------------------------------------------------
    teams = tree.cssselect('div.col-xs-4.col-sm-3.tablecell > h2 > a')
    teams = list(x.get('href') for x in teams)
    teams = extract_ids(teams)

    # If there was no ID to extract (i.e. it is not yet known who will play),
    # provide fake IDs
    ## TODO: Make this more robust
    if len(teams) == 0:
        teams = np.array([0, 0], dtype=np.int64)

    teams = pd.DataFrame(teams.reshape(1, 2),
                         columns=['Home', 'Away'])

    date = tree.cssselect('div.col-xs-4.col-sm-2.tablecell > div.date.khanded')
    date = date[0].text.strip()
    ## TODO: Make this more robust
    if len(date) == (10 + 2 + 5):
        date = datetime.strptime(date, '%d.%m.%Y, %H:%M')
    elif len(date) == 10:
        date = datetime.strptime(date, '%d.%m.%Y')
    else:
        date = None
    date = np.datetime64(date, 's')

    details = tree.cssselect('div.col-sm-6.col-md-5 > table')
    place = tree.cssselect('div.pagecontent > table.right-left.spacced')
    details = list(_parse_details_table(tab) for tab in details + place)
    if len(details) > 0:
        details = pd.concat(details, axis=1)
        details.insert(loc=0, column='Date', value=date)
    else:
        details = pd.DataFrame([date], columns=['Date'])

    details = pd.concat([ids, teams, details], axis=1)

    # Statistics --------------------------------------------------------------
    stat_tabs = tree.cssselect('table.rs-standings-table')

    if len(stat_tabs) > 0:
        stats = pd.concat(list(_parse_stats_table(tab, season=season)
                               for tab in stat_tabs),
                          ignore_index=True)
        stats = vsu.df_colattach1(ids, stats)
    else:
        stats = []

    # Results -----------------------------------------------------------------
    rslt_tab = tree.cssselect('table#gameScore_' + str(ID))
    if len(rslt_tab) > 0:
        results = _parse_results_table(rslt_tab[0])
        results = vsu.df_colattach1(ids, results)
    else:
        results = []

    # Return values -----------------------------------------------------------
    rslt = {'information': details,
            'results': results,
            'stats': stats}

    return rslt


def batch_fetch_match_info(combinations):
    """
    Runs a lower level function for all combinations and concatenates DataFrames.
    """
    # TODO: The interface should be reviewed here, simply a draft below
    # Maybe it can be done a little bit smarter
    combinations = combinations.loc[:, ['League', 'Season', 'MatchID']]
    data = list(fetch_match_info(*x) for x in combinations.values)

    rslt = dict()
    for key in data[0].keys():
       tables = list(x[key] for x in data if len(x[key]) > 0)

       if len(tables) > 0:
           rslt[key] = pd.concat(tables,
                                 ignore_index=True)
       else:
           rslt[key] = list()

    return rslt


# %% All
def fetch_all(league, season):
    tabs = dict()
    tabs['matches_list'] = fetch_matches(league, season)
    matches_data = batch_fetch_match_info(tabs['matches_list'])
    tabs['matches_info'] = matches_data['information']
    tabs['matches_stats'] = matches_data['stats']
    tabs['matches_results'] = matches_data['results']

    tabs['teams_list'] = fetch_teams(league, season)
    teams_data = batch_fetch_team_info(tabs['teams_list'])
    tabs['teams_info'] = teams_data['information']
    tabs['teams_roster'] = teams_data['roster']

    tabs['players_list'] = fetch_players(league, season)
    # Since players come and go, the full players list should be extended
    # by all players from statistics
    plist_stats = tabs['matches_stats'][['League', 'Season', 'PlayerID']]
    tabs['players_list'] = pd.concat([tabs['players_list'], plist_stats],
                                     ignore_index=True).drop_duplicates()
    tabs['players_list'] = tabs['players_list'].reset_index(drop=True)

    # Some matches with unnamed players in Stats pop-up
    # PlayerID = 0 crashes players_info, as it redirects to all players list
    tabs['players_list'] = tabs['players_list'].query('PlayerID > 0')

    tabs['players_info'] = batch_fetch_player_info(tabs['players_list'])

    return tabs
