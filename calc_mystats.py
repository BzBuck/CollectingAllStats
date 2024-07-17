import pandas as pd
import requests

csv_import = 'allscraped.csv'

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

def to_totals(df,stat):
    df[f"{stat}_Totals"] = df[stat]*df["GamesPlayed"]
    return df

# Read all of the data from a csv
# It should automatically convert types correctly
read_df = pd.read_csv(csv_import)

def req_filter(df, stat, min_value):
    df = df[df[stat] > min_value]
    return df

# Common Stats
common = ["Name","TeamAbbreviation","GamesPlayed","Minutes","POINTS","REB","AST","STL","BLK"]

# Create minutes filter and write to csv
# 1000 minutes is the equivalent of 20 minutes per game in 50 games
filtered_df = req_filter(read_df,"Minutes",1000)

filtered_df.to_csv("filtered.csv")

my_stats = pd.DataFrame()
my_stats = filtered_df[["Name","TeamAbbreviation","GamesPlayed","Minutes","POINTS","AST","REB","AST_POINTS_CREATED","AST_ADJ","POTENTIAL_AST","PASSES_MADE","SECONDARY_AST","FT_AST"]]

my_stats["PointsPerAssist"] = my_stats["AST_POINTS_CREATED"] / my_stats["AST"]
my_stats["AdjustedAssistPtsCreated"] = my_stats["PointsPerAssist"] * my_stats["AST_ADJ"]
my_stats["PotentialAssistPtsCreated"] = my_stats["PointsPerAssist"] * my_stats["POTENTIAL_AST"]
my_stats["MissedAssists"] = my_stats["POTENTIAL_AST"] - my_stats["AST"]
my_stats["MissedAssistsPerAssist"] = my_stats["MissedAssists"] / my_stats["AST"]
my_stats["PotentialAssistsPerPass"] = my_stats["POTENTIAL_AST"] / my_stats["PASSES_MADE"]
my_stats["AdjustedPotentialAssistPtsCreated"] = my_stats["PointsPerAssist"] * (my_stats["POTENTIAL_AST"] + my_stats["SECONDARY_AST"] + my_stats["FT_AST"])
my_stats["FTAssistsPerAssist"] = my_stats["FT_AST"] / my_stats["AST"]
my_stats["2ndAssistsPerAssist"] = my_stats["SECONDARY_AST"] / my_stats["AST"]



my_stats = filtered_df[common]

# True Stocks
my_stats["TrueStock"] = filtered_df["RecoveredBlocks"] + filtered_df["Steals"] + filtered_df["Offensive Fouls Drawn"]  + filtered_df["Charge Fouls Drawn"]
my_stats = to_per_game(my_stats,"TrueStock")


# Rebounding
my_stats["OREB"] = filtered_df['OREB']
my_stats["DREB"] = filtered_df['DREB']
my_stats["C_OREB"] = filtered_df['C_OREB']
my_stats["C_DREB"] = filtered_df['C_DREB']

my_stats['C_OREB_PCT'] = my_st