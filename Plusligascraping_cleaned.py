#!/usr/bin/env python
# coding: utf-8

# In[1]:


from bs4 import BeautifulSoup
# from selenium import webdriver
import pandas as pd
import requests
import lxml.html as lh
import re
import numpy as np
from tqdm import tqdm_notebook as tqdm

import seaborn as sns


# In[3]:


#scraping danych o siatkarzach PL - wyznaczamy ID siatkarzy do zebrania o nich informacji

url_pattern = "https://www.plusliga.pl/players/tour/{}.html?memo=%7B%22players%22%3A%7B%22mainFilter%22%3A%22letter%22%2C%22subFilter%22%3A%22all%22%7D%7D"
years = np.arange(2022,2023,1)
players_id_total = pd.DataFrame([])
players_id = []
for i in years:
    url = url_pattern.format(i)
    odpowiedz = requests.get(url)
    html_doc = odpowiedz.text
    soup = BeautifulSoup(html_doc, "html5lib")
    odpowiedz = requests.get(url)    
    for link in soup.findAll('a'):
        try:           
            if 'players' in link.get('href').split('/') and 'id' in link.get('href').split('/'):
                players_id.append(re.findall(r'\d{1,9}',link.get('href')))
                
        except:
            continue
players_id_2022 = pd.DataFrame(players_id)
#players_id_2021.to_csv(r'C:\Users\Zyll\Documents\players_id.csv', encoding = 'utf-8-sig')

players_id = players_id_2022[0]
players_id = players_id_2022.drop_duplicates()
players_id


# In[5]:


#sprawdzam rezultat na jednym graczy 
id_list = np.unique(players_id[0])

url = 'https://www.plusliga.pl/players/id/2100071.html'
html_doc = requests.get(url).text
soup = BeautifulSoup(html_doc, "html5lib")

wzrost = soup.findAll('div',class_ = "datainfo text-center")[0].find('span').text
waga = soup.findAll('div',class_ = "datainfo text-center")[1].find('span').text
zasieg = soup.findAll('div',class_ = "datainfo text-center")[2].find('span').text
data_urodzenia = soup.findAll('div',class_ = "datainfo small")[0].find('span').text

wzrost


# In[4]:


pd.DataFrame(players_id).drop_duplicates()[0][0:5]


# In[6]:


#zbieram dane o wszystkich graczach i eksportuje do csv
url_pattern= 'https://www.plusliga.pl/players/id/{}.html'
player_data = []
player_data = pd.DataFrame(player_data)

for i in tqdm(pd.DataFrame(players_id)[0]):
    try:    

        url = url_pattern.format(i)
        odpowiedz = requests.get(url)
        html_doc = odpowiedz.text
        soup = BeautifulSoup(html_doc, "html5lib")

        a = pd.read_html(html_doc)
        a = a[0].dropna(axis=0, thresh=4)
        imie_nazw = soup.findAll('h1')[0].text
        a["imie_nazw"] = imie_nazw
        a["wzrost"] = soup.findAll('div',class_ = "datainfo text-center")[0].find('span').text
        a["waga"] = soup.findAll('div',class_ = "datainfo text-center")[1].find('span').text
        a["zasieg"] = soup.findAll('div',class_ = "datainfo text-center")[2].find('span').text
        a["data_urodzenia"] = soup.findAll('div',class_ = "datainfo small")[0].find('span').text
        player_data = pd.concat([player_data,a])
        player_data
    except:
        continue

player_data


# In[15]:


player_data.to_excel(r'players_data_2022.xlsx', encoding = 'utf-8-sig')


# In[7]:


#wyciagniecie wyników spotkań
url_pattern= 'https://www.plusliga.pl/games/id/{}'
# total_stats = []
total_stats = pd.DataFrame([])

for i in tqdm(games_id): 
    try:
        url = url_pattern.format(i)
        odpowiedz = requests.get(url)
        html_doc = odpowiedz.text
        soup = BeautifulSoup(html_doc, "html5lib")
        home_team = soup.findAll('h3')[-5].text
        away_team = soup.findAll('h3')[-4].text
        data = soup.findAll("div",class_ = "date khanded")[-1].text
        stats_rows = []
        tables = pd.read_html(html_doc)
        results = pd.DataFrame(tables[2])
        results["home_team"] = home_team
        results["away_team"] = away_team
        results["data"] = data
        
        total_stats = total_stats.append(results)
    except:
        continue
    
total_stats
# total_stats.to_csv(r'C:\Users\Zyll\Documents\total_stats2018_20.csv', encoding = 'utf-8-sig') #zapisuje zrzucone dane do csv


# In[5]:


#wydobywam listę id spotkań z sezonu 2021/22
years = np.arange(2022,2023,1) #lata ktore mnie interesuja, tworze liste

url_pattern= "https://plusliga.pl/games/tour/{}.html?memo=%7B\"games\"%3A%7B%7D%7D"
id_list = []
for i in years:
    url = url_pattern.format(i)
    odpowiedz = requests.get(url)
    html_doc = odpowiedz.text
    soup = BeautifulSoup(html_doc, "html5lib")
       
    for link in soup.findAll('a'):
        try:
            if 'games' in link.get('href').split('/'):
                id_list.append(re.findall(r'\d{7}',link.get('href')))
        except:
            continue
    a = pd.DataFrame(id_list)
    a = a.rename({0: 'id_match'},axis=1)
    a.drop_duplicates().sort_values(by="id_match").reset_index(drop = True)
    
games_id2 = a.id_match.drop_duplicates()

games_id2.sort_values()


# In[7]:


games_id2 = [1102216,1102217,1102195,1102377,1102218,1102196,1102197,1102198]


# In[8]:


#wyciagniecie statystyk
url_pattern= 'https://www.plusliga.pl/games/id/{}'
total_stats = []
total_stats = pd.DataFrame(total_stats)

for i in tqdm(games_id2): 
    url = url_pattern.format(i)
    odpowiedz = requests.get(url)
    html_doc = odpowiedz.text
    soup = BeautifulSoup(html_doc, "html5lib")
    home_team = soup.findAll('h3')[-3].text
    away_team = soup.findAll('h3')[-2].text
    data = soup.findAll("div",class_ = "date khanded")[-1].text
    stats_rows = []
    try:    
        for j in range(0,2):
            stats = soup.findAll("table", class_ = "rs-standings-table")[j]
            stats.findAll('tr')

            for row in stats.findAll('tr'): #pętla przez wszystkie tagi tr, czyli wiersze
                stats_cells = [] #pusta lista komórek
                for cell in row.findAll(["th","td"]): #pętla przez wszystkie tagi th = headers, td = data
                    text = cell.text #z każdego wiersza z th i td w tabeli wywołujemy zawarty w nich tekst
                    stats_cells.append(text) #appendujemy znaleziony tekst do wiersza
                stats_rows.append(stats_cells) #appendujemy cały wiersz
        a = pd.DataFrame(stats_rows)
        a["home_team"] = home_team
        a["away_team"] = away_team
        a["data"] = data
        total_stats = pd.concat([total_stats,a])
    except:
        continue
total_stats
# total_stats.to_csv(r'C:\Users\Zyll\Documents\total_stats2018_20.csv', encoding = 'utf-8-sig') #zapisuje zrzucone dane do csv


# In[9]:


total_stats.to_csv(r'total_stats2022.csv', encoding = 'utf-8-sig') #zapisuje zrzucone dane do csv


# In[10]:


#oczyszczamy dane

df = pd.read_csv(r'total_stats2022.csv') #wywoluje plik
df.drop([0,1],axis=0,inplace=True) #usuwam 1 dwa wiersze
df.drop("Unnamed: 0", axis=1, inplace=True) #usuwam kolumnę "unnamed: 0"
df.rename({"0":"imie_nazw","1": "set_1","2": "set_2","3": "set_3","4": "set_4","5": "set_5"}, axis = 1,inplace = True) #zmieniam nazwy kolumn z pozycjami w setach
df.rename({"6": "total_pkt","7": "BP","8": "ratio","9": "liczba_zagr","10":"błędy_zagr"}, axis = 1,inplace = True) #zmieniam nazwy kolumn nr 2
df.rename({"11": "asy","12": "eff_zagr","13": "liczba_przyj","14": "bledy_przyj","15":"% poz","16":"% perf"}, axis = 1,inplace = True)
df.rename({"17": "liczba_atak","18": "błędy_atak","19": "zablok_atak","20": "skut_atak","21":"%skut_atak","22":"%eff_atak","23":"bloki","24":"wybloki"}, axis = 1,inplace = True)
df = df.drop(df[df['imie_nazw']== "Łącznie"].index) #usunięcie wierszy, gdzie w imie_nazw = Łącznie
df = df.drop(df[df['imie_nazw'].map(len) <3].index) #usunięcie wierszy, gdzie w imie_nazw mniej znakow niz 3
df["imie_nazw"]= df.imie_nazw.str.replace('\t',"")
df["imie_nazw"]= df.imie_nazw.str.replace('\n',"")
df["imie_nazw"]= df.imie_nazw.str.replace(r"\(.*\)","")
df["imie_nazw"]= df.imie_nazw.str.strip()

df["data"]= df.data.str.replace('\t',"")
df["data"]= df.data.str.replace('\n',"")
df["data"]= df.data.str.replace(r"\(.*\)","")
df["data"]= df.data.str.strip()

df["numer_zawodnika"] = df["imie_nazw"].str[0:3] #pierwsze 3 znaki z kolumny to numer
df["numer_zawodnika"] = df["numer_zawodnika"].map(str.strip) #oczyszczamy liczby ze spacji

df["imie_nazw"]= df.imie_nazw.str[3:] #usuwamy pierwsze 3 znaki z imie_nazw == numery zawodnikow
df["imie_nazw"]= df.imie_nazw.str.strip()
df["data_2"]= df.data.str[:10] #usuwamy pierwsze 3 znaki z imie_nazw == numery zawodnikow
df["data_2"] = pd.to_datetime(df.data_2, format = '%d.%m.%Y')
df["data"] = pd.to_datetime(df.data, format = '%d.%m.%Y, %H:%M')
df["liczba_przyj"] = np.where(df["liczba_przyj"]=="-",0,df["liczba_przyj"]).astype('float')
df["% poz"] = np.where(df["% poz"]=="-",0,df["% poz"])
df["% poz"] = df['% poz'].str.rstrip('%').astype('float') / 100.0
df["% perf"] = np.where(df["% perf"]=="-",0,df["% perf"])
df["% perf"] = df['% perf'].str.rstrip('%').astype('float') / 100.0
# df["liczba_przyj"] = df['liczba_przyj'].str.astype('float')
df["przyj_poz"] = (df["% poz"]*df["liczba_przyj"]).round(0)
df["perf_poz"] = (df["% perf"]*df["liczba_przyj"]).round(0)
df['sety'] = df[["set_1","set_2","set_3","set_4","set_5"]].count(axis=1)


bins_dt = pd.date_range('2008-09-01', freq='365D', periods=15)
bins_str = bins_dt.astype(str).values
labels = ['{}/{}'.format(bins_str[i-1][:4], bins_str[i][:4]) for i in range(1, len(bins_str))]
df["sezon"] = pd.cut(df.data_2.astype(np.int64)//10**9,
                   bins=bins_dt.astype(np.int64)//10**9,
                   labels=labels)

df.to_excel(r'total_stats_2022_cleaned.xlsx', encoding = 'utf-8-sig') #zapisuje zrzucone dane do csv


# In[11]:


df1 = pd.read_excel(r'total_stats_2022_cleaned.xlsx') #wywoluje plik z danymi
df2 = pd.read_excel(r'players_data_2022.xlsx') #wywoluje plik z danymi siatkarzy
df3 = pd.merge(df1, df2, on="imie_nazw", how = "left") #left join po nazwisku
df3.to_excel(r'total_stats_2022_cleaned_with_teams.xlsx', encoding = 'utf-8-sig') #zapisuje zrzucone dane do xlsx


# In[54]:


df.to_csv(r'C:\Users\Zyll\Documents\total_stats2008_2020_cleaned.csv', encoding = 'utf-8-sig') #zapisuje zrzucone dane do csv

