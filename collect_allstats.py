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



# Scrape pbpstats
# https://github.com/dblackrun/pbpstats-api-code-examples/blob/main/get-totals.ipynb
def get_pbp(season, season_type, target, stat="get-totals", ):
    url = f"https://api.pbpstats.com/{stat}/nba"
    params = {
        "Season": season,
        "SeasonType": season_type,
        "Type": target
    }
    response = requests.get(url, params=params)
    response_json = response.json()
    player_stats = response_json["multi_row_table_data"]
    
    df = pd.json_normalize(player_stats)
    df.fillna(0, inplace=True)
    return df.rename(columns={'EntityId': 'PlayerId'})


pbp = get_pbp(season,"Regular Season", "Player")

pbpteam = get_pbp(season,"Regular Season", "Team")
pbpteam.columns = ['Team' + col if not col.startswith('Team') else col for col in pbpteam.columns]

pbpteam.to_csv("pbpteam.csv")

pbp = pd.merge(pbp,pbpteam, on='TeamAbbreviation', how='left')

# https://api.pbpstats.com/get-totals/wnba?Season=2022&SeasonType=Regular%20Season&Type=Player&StarterState=All&StartType=All

# URL Features
stat_endpoint = "leaguedashptstats" #leaguehustlestatsplayer
url = f"https://stats.nba.com/stats/" 

# Set params to desired 
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
myparams["PerMode"] = "PerGame" # "PerGame" "Totals" 
myparams["SeasonType"] = "Regular Season" # "Playoffs" "Regular%20Season"


def params_to_url(base_url,endpoint, params):
    url = f"{base_url}{endpoint}?"

    # Loop through and add all params to the url
    for param in params: 
        url += f"{param}={params[param]}&"
    
    return url[:-1]

def request_data(url,headers=STATS_HEADERS):
    response = requests.get(url, headers=headers)
    data = response.json()
    my_players_df = pd.DataFrame(data['resultSets'][0]['rowSet'], columns=data['resultSets'][0]['headers'])
    return my_players_df.rename(columns={'PLAYER_ID': 'PlayerId'})


def mergedfs(df1, df2):
    # Ensure 'PlayerId' is of type int64 in both dataframes
    df1['PlayerId'] = df1['PlayerId'].astype('int64')
    df2['PlayerId'] = df2['PlayerId'].astype('int64')

    # Merge the dataframes on 'PlayerId' using poor suffix append since pandas suffix duplicates broke
    merged_df = pd.merge(df1, df2, on='PlayerId',how="left",suffixes=df2.keys()[-2:])

    return merged_df

# Set new param and add it to the full merged dataframe
# Example req_url: https://stats.nba.com/stats/leaguedashptstats?PtMeasureType=Possessions&Season=2023-24
myparams["PtMeasureType"] = "Possessions"
req_url = params_to_url(url,stat_endpoint,myparams)
reqdatar = request_data(req_url)
mrgd = mergedfs(pbp,reqdatar)

# I am using sloppy run ons for concision but this operates the same as above
myparams["PtMeasureType"] = "Passing"
mrgd = mergedfs(mrgd,request_data(params_to_url(url,stat_endpoint,myparams)))

myparams["PtMeasureType"] = "Defense"
mrgd = mergedfs(mrgd,request_data(params_to_url(url,stat_endpoint,myparams)))

myparams["PtMeasureType"] = "SpeedDistance"
mrgd = mergedfs(mrgd,request_data(params_to_url(url,stat_endpoint,myparams)))

myparams["PtMeasureType"] = "Rebounding"
mrgd = mergedfs(mrgd,request_data(params_to_url(url,stat_endpoint,myparams)))


myparams["PtMeasureType"] = ""
myparams["DefenseCategory"] = "Overall"
myparams["PlayerID"] = 0

myparams["PlayerId"] = ""

stat_endpoint = "leaguedashptdefend"
mrgd = pd.merge(mrgd, request_data(params_to_url(url,stat_endpoint,myparams)), on='PLAYER_NAME')

stat_endpoint = "leaguehustlestatsplayer"
mrgd = mergedfs(mrgd,request_data(params_to_url(url,stat_endpoint,myparams)))

# Estimated Advanced
# For some reason this one url has different keys for only one resultSet and heeaders so I have to change it manually
# Ideally I will eventually calculate these myself since this code is so clunky and inconvinient
response = requests.get("https://stats.nba.com/stats/playerestimatedmetrics?LeagueID=00&Season=2019-20&SeasonType=Regular+Season",headers=STATS_HEADERS)
data = response.json()
headers = data['resultSet']['headers']
rows = data['resultSet']['rowSet']
players_est_df = pd.DataFrame(rows, columns=headers)
players_est_df.set_index(headers[0], inplace=True)
mrgd["PLAYER_NAME"] = mrgd["Name"]
mrgd =  pd.merge(mrgd, players_est_df, on='PLAYER_NAME')


mrgd.to_csv("allscraped.csv")