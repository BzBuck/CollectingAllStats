import pandas as pd
import requests

csv_import = 'allscraped.csv'

# Convert Totals to other forms
def to_per_100pos(df,stat):
    return df[stat]/df["TotalPoss"]*100 # PARTIAL_POSS

def to_per_game(df,stat,games = "GamesPlayed"):
    return df[stat]/df[games]

def to_per_36_min(df,stat):
    return df[stat]/df["Minutes"]*36 

def to_totals(df,stat):
    df[f"{stat}_Totals"] = df[stat]*df["GamesPlayed"]
    return df

# Normalize between eras by the averages of teams
def normalize_(df,stat):
    # Standards for team totals
    PTS = 100 / df["PTS"]
    AST = 25 / df["AST"]
    REB = 45 / df["REB"]
    STL = 8 / df["STL"]
    BLK = 8 / df["BLK"]
    return [PTS,AST,REB,STL,BLK]

# Read all of the data from a csv
# It should automatically convert types correctly
read_df = pd.read_csv(csv_import)

def req_filter(df, stat, min_value):
    df = df[df[stat] > min_value]
    return df

# Common Stats
common = ["Name","TeamAbbreviation","GamesPlayed","Minutes","Points","REB","AST","STL","BLK"]

# Create minutes filter and write to csv
# 1000 minutes is the equivalent of 20 minutes per game in 50 games
filtered_df = req_filter(read_df,"Minutes",1000)

filtered_df.to_csv("filtered.csv")

my_stats = pd.DataFrame()
my_stats = filtered_df[["Name","TeamAbbreviation","GamesPlayed","Minutes","Points","Assists","Rebounds","Steals","Blocks","Turnovers","Fouls","AST_POINTS_CREATED","AST_ADJ","POTENTIAL_AST","PASSES_MADE","SECONDARY_AST","FT_AST","TsPct"]]

my_stats["TOV"] = my_stats["Turnovers"] / my_stats["GamesPlayed"]
my_stats["PF"] = my_stats["Fouls"] / my_stats["GamesPlayed"]
my_stats["PTS"] = my_stats["Points"] 

# Scoring stats
my_stats["TrueShotAttempts"] = my_stats["PTS"] / (2 * my_stats["TsPct"])
my_stats["EstimatedPointsPerAttempt"] = 2 * my_stats["TsPct"]

# my_stats["TrueScoring"] = my_stats["AST_POINTS_CREATED"] / my_stats["AST"]

# Assist stats
my_stats["PointsPerAssist"] = my_stats["AST_POINTS_CREATED"] / my_stats["Assists"]
my_stats["AdjustedAssistPtsCreated"] = my_stats["PointsPerAssist"] * my_stats["AST_ADJ"]
my_stats["PotentialAssistPtsCreated"] = my_stats["PointsPerAssist"] * my_stats["POTENTIAL_AST"]
my_stats["MissedAssists"] = my_stats["POTENTIAL_AST"] - my_stats["Assists"]
my_stats["MissedAssistsPerAssist"] = my_stats["MissedAssists"] / my_stats["Assists"]
my_stats["PotentialAssistsPerPass"] = my_stats["POTENTIAL_AST"] / my_stats["PASSES_MADE"]
my_stats["FTAssistsPerAssist"] = my_stats["FT_AST"] / my_stats["Assists"]
my_stats["2ndAssistsPerAssist"] = my_stats["SECONDARY_AST"] / my_stats["Assists"]
my_stats["AssistTsPct"] = my_stats["AST_POINTS_CREATED"] /  my_stats["PotentialAssistPtsCreated"]
my_stats["AdjustedAssistTsPct"] = my_stats["AdjustedAssistPtsCreated"] /  my_stats["PotentialAssistPtsCreated"]

# Usage Stats
my_stats["UsagePct"] = filtered_df['Usage'] / 100
my_stats["PointsContributed"] = my_stats["PTS"] + my_stats["AdjustedAssistPtsCreated"]
my_stats["PossessionEndAttempts"] = my_stats["TrueShotAttempts"] + my_stats["TOV"] + my_stats["POTENTIAL_AST"] 
my_stats["PointsPerPossessionEndAttempt"] = my_stats["PTS"] / my_stats["PossessionEndAttempts"]
my_stats["PointsContributedPerPossessionEndAttempt"] = my_stats["PointsContributed"] / my_stats["PossessionEndAttempts"]
my_stats["PointsOverOpponent"] = filtered_df["Points"] / filtered_df["OpponentPoints"]
my_stats["PointsOverOpponentPer100"] = my_stats["PointsOverOpponent"] * 100
my_stats["Touches"] = filtered_df['TOUCHES']
my_stats["PossTime"] = filtered_df['AVG_SEC_PER_TOUCH']
my_stats["PossEndsAttemptsPerTouch"] = my_stats["PossessionEndAttempts"] / my_stats["Touches"]
my_stats["PossEndAttemptsPct"] = my_stats["PossessionEndAttempts"] / to_per_game(filtered_df,"TeamOffPoss",games = "TeamGamesPlayed") # Usage Percent Replacement


# Defensive stats
my_stats["TrueStock"] = filtered_df["RecoveredBlocks"] + filtered_df["Steals"] + filtered_df["Offensive Fouls Drawn"]  + filtered_df["Charge Fouls Drawn"]
my_stats["TrueStock_PerGame"] = to_per_game(my_stats,"TrueStock")
my_stats["RecoveredBlocks"] = filtered_df["RecoveredBlocks"] 
my_stats["RecoveredBlocks_PerGame"] = to_per_game(my_stats,"RecoveredBlocks")
my_stats["ContestedShots"] = filtered_df["CONTESTED_SHOTS"]
my_stats["DefendedShots"] = filtered_df["D_FGA"]
my_stats["BlocksPerContest"] = my_stats["Blocks"] / my_stats["ContestedShots"]# Contested shots means hand up, Defended FGA means any defense. all contested shots are DFGAs
my_stats["RecoveredBlocksPerContest"] = my_stats["RecoveredBlocks_PerGame"] / my_stats["ContestedShots"] 
my_stats["Questions"]  = my_stats["ContestedShots"] / my_stats["DefendedShots"]
my_stats["BlocksPerDefense"] = my_stats["Blocks"] / my_stats["DefendedShots"]
my_stats["RecoveredBlocksPerDefense"] = my_stats["RecoveredBlocks_PerGame"] / my_stats["DefendedShots"]
my_stats["TrueStockPerDefense"] = my_stats["TrueStock_PerGame"] / my_stats["DefendedShots"]

# # Rebounding
my_stats["OREB"] = filtered_df['OREB']
my_stats["DREB"] = to_per_game(filtered_df,"DefRebounds")
my_stats["C_DREB"] = filtered_df['DREB_CONTEST']
my_stats["PositiveRebPoss"] = filtered_df['DREB_CONTEST'] + my_stats["OREB"]
my_stats["EstimatedGainedRebPts"] = my_stats["PositiveRebPoss"] * my_stats["PointsContributedPerPossessionEndAttempt"]
my_stats["PointsContributedWithReb"] = my_stats["PointsContributed"] + my_stats["EstimatedGainedRebPts"]
my_stats["FullExpectedPointsContribution"] = my_stats["PointsContributedWithReb"] / my_stats["PossessionEndAttempts"]

#ORB > gained possession
#CDRB > taken possession.
# Getting a CDREB is the opposite of ORB


# Game Score was created by John Hollinger to give a rough measure of a player's productivity for a single game. 
# The scale is similar to that of points scored, (40 is an outstanding performance, 10 is an average performance, etc.).
#GmSc - Game Score; the formula is 
#                           PTS       + 0.4 * FG                                                                     - 0.7 * FGA                                                                 - 0.4 * (FTA - FT)                                                             + 0.7 * ORB              + 0.3 * DRB              + STL                + 0.7 * AST                 + 0.7 * BLK                - 0.4 * PF             - TOV. 
my_stats["GmSc"] = my_stats["Points"] +  (0.4 * (to_per_game(filtered_df,"FG2M") + to_per_game(filtered_df,"FG3M"))) - 0.7 * (to_per_game(filtered_df,"FG2A") + to_per_game(filtered_df,"FG3A")) - 0.4 * (to_per_game(filtered_df,"FTA") - to_per_game(filtered_df,"FtPoints")) + 0.7 * my_stats["OREB"] + 0.3 * my_stats["DREB"] + my_stats["Steals"] + 0.7 * my_stats["Assists"] + 0.7 * my_stats["Blocks"] - 0.4 * my_stats["PF"] - my_stats["TOV"]


# Plus Minus stat
my_stats["+-/m"] = filtered_df['PlusMinus'] / filtered_df['Minutes']
my_stats["+-/48m"] = filtered_df['PlusMinus'] / filtered_df['Minutes'] * 48
my_stats["TeamPlusMinus/48"] = filtered_df['TeamPlusMinus'] /82
my_stats["TeamPlusMinus/m"] = my_stats["TeamPlusMinus/48"] / 48
my_stats["PlayerOff+-"] = my_stats["+-/48m"] - my_stats["TeamPlusMinus/48"]

my_stats = my_stats.round(3)
my_stats.to_csv("mystats.csv")