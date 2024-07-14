import pandas as pd
import requests


year = 2024
season = f"{year - 1}-{year % 100:02}" 

# Get full headers if necessary
try:
    from nba_api.library.debug.debug import STATS_HEADERS
except ImportError:
    STATS_HEADERS = {
        "Host": "stats.nba.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "x-nba-stats-origin": "stats",
        "x-nba-stats-token": "true",
        "Connection": "keep-alive",
        "Referer": "https://stats.nba.com/",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }


# Convert Totals to other forms
def to_per_100pos(df,stat):
    df[f"{stat}_Per100Pos"] = df[stat]/df["TotalPoss"]*100 # PARTIAL_POSS
    return df

def to_per_game(df,stat):
    df[f"{stat}_PerGame"] = df[stat]/df["GamesPlayed"]
    return df

def to_per_36_min(df,stat):
    df[f"{stat}_Per36Min"] = df[stat]/df["Minutes"]*36 
    return df

# Scrape pbpstats
def get_pbp(season, stat="get-totals"):
    url = f"https://api.pbpstats.com/{stat}/nba"
    params = {
        "Season": season,
        "SeasonType": "Regular Season",
        "Type": "Player"
    }
    response = requests.get(url, params=params)
    response_json = response.json()
    player_stats = response_json["multi_row_table_data"]
    player_stats
    df = pd.json_normalize(player_stats)
    df.fillna(0, inplace=True)
    return df

pbp = get_pbp(season)

pbp = pbp.rename(columns={'EntityId': 'PlayerId'})




# URL Features
stat_endpoint = "playerindex" #leaguehustlestatsplayer
url = f"https://stats.nba.com/stats/" 
myparams = {
    "College":"",
    "Conference":"",
    "Country":"",
    "DateFrom":"",
    "DateTo":"",
    "Division":"",
    "DraftPick":"",
    "DraftYear":"",
    "GameScope":"",
    "Height":"",
    "ISTRound":"",
    "LastNGames":0,
    "LeagueID":"00",
    "Location":"",
    "Month":0,
    "OpponentTeamID":0,
    "Outcome":"",
    "PORound":0,
    "PerMode":"PerGame",
    "PlayerExperience":"",
    "PlayerOrTeam":"Player",
    "PlayerPosition":"",
    "PtMeasureType":"Possessions",
    "Season":"2023-24",
    "SeasonSegment":"",
    "SeasonType":"Playoffs",
    "StarterBench":"",
    "TeamID":0,
    "VsConference":"",
    "VsDivision":"",
    "Weight":""

}


def params_to_url(base_url,endpoint, params):
    url = f"{base_url}{endpoint}?"
    for param in params:
        url += f"{param}={params[param]}&"
    
    return url[:-1]

def request_data(url,headers=STATS_HEADERS):
    response = requests.get(url, headers=headers)
    data = response.json()
    my_players_df = pd.DataFrame(data['resultSets'][0]['rowSet'], columns=data['resultSets'][0]['headers'])

    return my_players_df


def mergedfs(df1, df2):
    # Ensure 'PlayerId' is of type int64 in both dataframes
    df1['PlayerId'] = df1['PlayerId'].astype('int64')
    df2['PlayerId'] = df2['PlayerId'].astype('int64')

    # Merge the dataframes on 'PlayerId'
    merged_df = pd.merge(df1, df2, on='PlayerId')

    return merged_df


# Set params to desired 
myparams["PtMeasureType"] = "Possessions"
myparams["PerMode"] = "PerGame" # "PerGame" "Totals" 
myparams["SeasonType"] = "Regular Season" #"Playoffs" "Regular%20Season"

req_url = params_to_url(url,stat_endpoint,myparams)


reqdatar = request_data(req_url)
reqdatar = reqdatar.rename(columns={'PERSON_ID': 'PlayerId'})


mrgd = mergedfs(pbp,reqdatar)
mrgd.to_csv("allscraped.csv")