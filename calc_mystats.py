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
# Normalization Constants
PTS = 100
AST = 25 
REB = 45
STL = 8
BLK = 8 


# Read all of the data from a csv
# It should automatically convert types correctly
read_df = pd.read_csv(csv_import)

def multi_filter(df,stats,min_values):
    if len(stats) == 1:
        return (df[stats[0]] >= min_values[0])
    else:
        return (df[stats[0]] >= min_values[0]) | (multi_filter(df,stats[1:],min_values[1:]))

# Common Stats
common = ["Name","TeamAbbreviation","GamesPlayed","Minutes","Points","REB","AST","STL","BLK"]

# Create minutes filter and write to csv
# 1000 minutes is the equivalent of 20 minutes per game in 50 games
filtered_df = read_df[multi_filter(read_df,["Minutes"], [1000])]

filtered_df.to_csv("filtered.csv")

my_stats = pd.DataFrame()
my_stats = filtered_df[["Name","TeamAbbreviation","GamesPlayed","Minutes","Points","Assists","Rebounds","Steals","Blocks","Turnovers","Fouls","TsPct"]]

my_stats["PTS"] = my_stats["Points"]        / my_stats["GamesPlayed"]
my_stats["REB"] = my_stats["Rebounds"]      / my_stats["GamesPlayed"]
my_stats["AST"] = my_stats["Assists"]       / my_stats["GamesPlayed"]
my_stats["STL"] = my_stats["Steals"]        / my_stats["GamesPlayed"]
my_stats["BLK"] = my_stats["Blocks"]        / my_stats["GamesPlayed"]
my_stats["TOV"] = my_stats["Turnovers"]     / my_stats["GamesPlayed"]
my_stats["FLS"] = my_stats["Fouls"]         / my_stats["GamesPlayed"]
my_stats["FTA"] = filtered_df["FTA"]        / my_stats["GamesPlayed"]
my_stats["FTM"] = filtered_df["FtPoints"]   / my_stats["GamesPlayed"]


# Winning
my_stats.loc[:, "Wins"] = filtered_df["W"]
my_stats.loc[:, "Losses"] = filtered_df["L"]
my_stats.loc[:, "WinPct"] = my_stats["Wins"] / (my_stats["Wins"] + my_stats["Losses"])
my_stats.loc[:, "TmWins"] = filtered_df["Team_W"]
my_stats.loc[:, "TmLosses"] = filtered_df["Team_L"]
my_stats.loc[:, "TmWinPct"] = filtered_df["Team_W/L%"]
my_stats.loc[:, "WinPctOfTeam"] = my_stats["Wins"] / (my_stats["TmWins"] + my_stats["TmLosses"])
my_stats.loc[:, "TmWinPctWithout"] = (my_stats["TmWins"] - my_stats["Wins"]) / (my_stats["TmWins"] + my_stats["TmLosses"] - (my_stats["Wins"] + my_stats["Losses"]))

# Win Scaled Basics
my_stats.loc[:,"TmWinReducedPTS"] = my_stats["PTS"] * my_stats["WinPctOfTeam"]
my_stats.loc[:,"TmWinReducedREB"] = my_stats["REB"] * my_stats["WinPctOfTeam"]
my_stats.loc[:,"TmWinReducedAST"] = my_stats["AST"] * my_stats["WinPctOfTeam"]


# Track Positions
positions = ["PG", "SG", "SF", "PF", "C"]
position_mapping = {pos: i+1 for i, pos in enumerate(positions)}
my_stats['Positions'] = filtered_df['Pos'].apply(lambda x: x.split('-') if isinstance(x, str) else [])
for pos in positions:
    my_stats[pos] = my_stats['Positions'].apply(lambda x: pos in x).astype(int)
my_stats['Positions'] = my_stats['Positions'].apply(lambda x: [position_mapping[pos] for pos in x])

# Scoring stats
my_stats["TrueShotAttempts"] = my_stats["PTS"] / (2 * my_stats["TsPct"])
my_stats["EstimatedPointsPerAttempt"] = 2 * my_stats["TsPct"]
my_stats["PaidPTS"] = my_stats["PTS"] - my_stats["FTM"]
# my_stats["TrueScoring"] = my_stats["AST_POINTS_CREATED"] / my_stats["AST"]

my_stats.loc[:, "TeamPP100"] = filtered_df["Team_Per100_PTS"]
my_stats.loc[:, "OppsPP100"] = filtered_df["Team_OppPer100_PTS"]
my_stats.loc[:, "PlayerPP100"] = my_stats["Points"]/filtered_df["TotalPoss"]


# Assist stats
my_stats.loc[:, "AST_POINTS_CREATED"] = filtered_df["AST_POINTS_CREATED"]
my_stats.loc[:, "AST_ADJ"] = filtered_df["AST_ADJ"]
my_stats.loc[:, "POTENTIAL_AST"] = filtered_df["POTENTIAL_AST"]
my_stats.loc[:, "Passes"] = filtered_df["PASSES_MADE"]
my_stats.loc[:, "SECONDARY_AST"] = filtered_df["SECONDARY_AST"]
my_stats.loc[:, "FT_AST"] = filtered_df["FT_AST"]

my_stats.loc[:, "PointsPerAssistAttempt"] = my_stats["AST_POINTS_CREATED"] / my_stats["POTENTIAL_AST"]
my_stats["PointsPerAssist"] = my_stats["AST_POINTS_CREATED"] / my_stats["AST"]
my_stats["AdjustedAssistPtsCreated"] = my_stats["PointsPerAssist"] * my_stats["AST_ADJ"] #*# How many estimated points were scored from the players assists of all types
my_stats["PotentialAssistPtsCreated"] = my_stats["PointsPerAssist"] * my_stats["POTENTIAL_AST"]
my_stats["MissedAssists"] = my_stats["POTENTIAL_AST"] - my_stats["AST"]
my_stats["MissedAssistsPerAssist"] = my_stats["MissedAssists"] / my_stats["Assists"]
my_stats["PotentialAssistsPerPass"] = my_stats["POTENTIAL_AST"] / my_stats["Passes"]
my_stats["FTAssistsPerAssist"] = my_stats["FT_AST"] / my_stats["Assists"]
my_stats["2ndAssistsPerAssist"] = my_stats["SECONDARY_AST"] / my_stats["Assists"]
my_stats["AssistTsPct"] = my_stats["AST_POINTS_CREATED"] /  my_stats["PotentialAssistPtsCreated"]
my_stats["AdjustedAssistTsPct"] = my_stats["AdjustedAssistPtsCreated"] /  my_stats["PotentialAssistPtsCreated"]

# Usage Stats
my_stats["UsagePct"] = filtered_df['Usage'] / 100
my_stats["PointsPerUse"] = my_stats["PTS"] / my_stats["UsagePct"] / 100
my_stats["PointsContributed"] = my_stats["PTS"] + my_stats["AdjustedAssistPtsCreated"]
my_stats["PossessionEndAttempts"] = my_stats["TrueShotAttempts"] + my_stats["TOV"] + my_stats["POTENTIAL_AST"] 
my_stats["PointsPerPossessionEndAttempt"] = my_stats["PTS"] / my_stats["PossessionEndAttempts"]
my_stats["PointsContributedPerPossessionEndAttempt"] = my_stats["PointsContributed"] / my_stats["PossessionEndAttempts"]
my_stats["PointsOverOpponent"] = filtered_df["Points"] / filtered_df["OpponentPoints"]
my_stats["PointsOverOpponentPer100"] = my_stats["PointsOverOpponent"] * 100
my_stats["PointsOverOpponentPerMan"] = my_stats["PointsOverOpponent"] * 5 # Relative to an individual 1/5 on court
my_stats["Touches"] = filtered_df['TOUCHES']
my_stats["PossTime"] = filtered_df['AVG_SEC_PER_TOUCH']
my_stats.loc[:, "DribblesPerTouch"] = filtered_df['AVG_DRIB_PER_TOUCH']
my_stats.loc[:, "FrontCrtTouches"] = filtered_df['FRONT_CT_TOUCHES']
my_stats.loc[:, "BackCrtTouches"] = filtered_df['TOUCHES'] - filtered_df['FRONT_CT_TOUCHES']
my_stats.loc[:, "DribblesPerGame"] = my_stats["DribblesPerTouch"] * my_stats["Touches"]
my_stats.loc[:, "DribblesPerPass"] = my_stats["DribblesPerTouch"] / my_stats["Passes"]
my_stats.loc[:, "PassesPerTouch"] = my_stats["Passes"] / my_stats["Touches"]
my_stats["PossEndsAttemptsPerTouch"] = my_stats["PossessionEndAttempts"] / my_stats["Touches"]
my_stats["PossEndAttemptsPct"] = my_stats["PossessionEndAttempts"] / to_per_game(filtered_df,"TeamOffPoss",games = "TeamGamesPlayed") # Usage Percent Replacement


# Defensive stats
my_stats["TrueStock"] = filtered_df["RecoveredBlocks"] + filtered_df["Steals"] + filtered_df["Offensive Fouls Drawn"]  + filtered_df["CHARGES_DRAWN"]
my_stats["TrueStock_PerGame"] = to_per_game(my_stats,"TrueStock")
my_stats["RecoveredBlocks"] = filtered_df["RecoveredBlocks"] 
my_stats["RecoveredBlocks_PerGame"] = to_per_game(my_stats,"RecoveredBlocks")
my_stats["ContestedShots"] = filtered_df["CONTESTED_SHOTS"]
my_stats["DefendedShots"] = filtered_df["D_FGA"]
my_stats["BlocksPerContest"] = my_stats["BLK"] / my_stats["ContestedShots"] # Contested shots means hand up, Defended FGA means any defense. all contested shots are DFGAs
my_stats["RecoveredBlocksPerContest"] = my_stats["RecoveredBlocks_PerGame"] / my_stats["ContestedShots"] 
my_stats["Questions"]  = my_stats["ContestedShots"] / my_stats["DefendedShots"] # How often is their hand up when defending a shot
my_stats["BlocksPerDefense"] = my_stats["BLK"] / my_stats["DefendedShots"]
my_stats["RecoveredBlocksPerDefense"] = my_stats["RecoveredBlocks_PerGame"] / my_stats["DefendedShots"]
my_stats["TrueStockPerDefense"] = my_stats["TrueStock_PerGame"] / my_stats["DefendedShots"]
my_stats["Deflections"] = filtered_df["DEFLECTIONS"]

# Rebounding
my_stats["OREB"] = filtered_df['OREB']
my_stats["DREB"] = to_per_game(filtered_df,"DefRebounds")
my_stats["C_DREB"] = filtered_df['DREB_CONTEST']
my_stats["ContestedReb"] = filtered_df['REB_CONTEST']
my_stats["PositiveRebPoss"] = filtered_df['DREB_CONTEST'] + my_stats["OREB"]
my_stats["EstimatedGainedRebPts"] = my_stats["PositiveRebPoss"] * my_stats["PointsContributedPerPossessionEndAttempt"]
my_stats["PointsContributedWithReb"] = my_stats["PointsContributed"] + my_stats["EstimatedGainedRebPts"]
my_stats["FullExpectedPointsContribution"] = my_stats["PointsContributedWithReb"] / my_stats["PossessionEndAttempts"]

#ORB > gained possession
#CDRB > taken possession.
# Getting a CDREB is the opposite of ORB

# Plus Minus stats
my_stats["+-/m"] = filtered_df['PlusMinus'] / filtered_df['Minutes']
my_stats["+-/48m"] = filtered_df['PlusMinus'] / filtered_df['Minutes'] * 48
my_stats["TeamPlusMinus/48"] = filtered_df['TeamPlusMinus'] / filtered_df['TeamGamesPlayed']
my_stats["TeamPlusMinus/m"] = my_stats["TeamPlusMinus/48"] / 48
my_stats["PlayerOff+-"] = my_stats["+-/48m"] - my_stats["TeamPlusMinus/48"]

# Game Ratings
my_stats["ORtg"] = filtered_df['OnOffRtg']
my_stats["DRtg"] = filtered_df['OnDefRtg']
my_stats.loc[:, "NRtg"] = my_stats["ORtg"] - my_stats["DRtg"]
my_stats["Team_ORtg"] = filtered_df['Team_ORtg']
my_stats["Team_DRtg"] = filtered_df['Team_DRtg']
my_stats["Team_NRtg"] = filtered_df['Team_NRtg']
my_stats["Player_Net_ORtg"] = my_stats["ORtg"] - my_stats["Team_ORtg"]
my_stats["Player_Net_DRtg"] = my_stats["DRtg"] - my_stats["Team_DRtg"]
my_stats["Player_Net_NRtg"] = my_stats["Player_Net_ORtg"] - my_stats["Player_Net_DRtg"]
my_stats["TeamGamesPlayed"] = filtered_df['TeamGamesPlayed']
my_stats["GamesMissed"] = my_stats["TeamGamesPlayed"] - my_stats["GamesPlayed"]
my_stats["GamesMissedPct"] = my_stats["GamesPlayed"] / my_stats["TeamGamesPlayed"]

# Game Score was created by John Hollinger to give a rough measure of a player's productivity for a single game. 
# The scale is similar to that of points scored, (40 is an outstanding performance, 10 is an average performance, etc.).
# GmSc - Game Score; the formula is 
#                           PTS       + 0.4 * FG                                                                  - 0.7 * FGA                                                                 - 0.4 * (FTA - FT)                                     + 0.7 * ORB              + 0.3 * DRB              + STL             + 0.7 * AST             + 0.7 * BLK             - 0.4 * PF              - TOV. 
my_stats["GmSc"] = my_stats["PTS"] +  (0.4 * (to_per_game(filtered_df,"FG2M") + to_per_game(filtered_df,"FG3M"))) - 0.7 * (to_per_game(filtered_df,"FG2A") + to_per_game(filtered_df,"FG3A")) - 0.4 * (my_stats["FTA"] - my_stats["FTM"]) + 0.7 * my_stats["OREB"] + 0.3 * my_stats["DREB"] + my_stats["STL"] + 0.7 * my_stats["AST"] + 0.7 * my_stats["BLK"] - 0.4 * my_stats["FLS"] - my_stats["TOV"]
my_stats.loc[:,"TmWinReducedGmSc"] = my_stats["GmSc"] * my_stats["WinPctOfTeam"]

# Fantasy stats
my_stats["FantaPTS"] = my_stats["PTS"] * 1.0
my_stats["FantaREB"] = my_stats["REB"] * 1.2
my_stats["FantaAST"] = my_stats["AST"] * 1.5
my_stats["FantaBLK"] = my_stats["BLK"] * 3.0
my_stats["FantaSTL"] = my_stats["STL"] * 3.0
my_stats["FantaTOV"] = my_stats["TOV"] * -1.0
my_stats["FantasyPts"] = my_stats["FantaPTS"] + my_stats["FantaREB"] + my_stats["FantaAST"] + my_stats["FantaBLK"] + my_stats["FantaSTL"] + my_stats["FantaTOV"]
my_stats["FantasyTot"] = my_stats["FantasyPts"] * my_stats["GamesPlayed"]

# ESPN Fantasy
my_stats["ESPNFantaPTS"] = my_stats["PTS"] * 1 
my_stats["ESPNFantaREB"] = my_stats["REB"] * 1
my_stats["ESPNFantaAST"] = my_stats["AST"] * 2
my_stats["ESPNFantaBLK"] = my_stats["BLK"] * 4
my_stats["ESPNFantaSTL"] = my_stats["STL"] * 4
my_stats["ESPNFantaTOV"] = my_stats["TOV"] * -2
my_stats["ESPNFantaFGS"] = to_per_game(filtered_df,"FG2M") * 2 + to_per_game(filtered_df,"FG3M") * 3 - (to_per_game(filtered_df,"FG2A") + to_per_game(filtered_df,"FG3A")) * 1

my_stats["ESPNFantasyPts"] = my_stats["FantaPTS"] + my_stats["FantaREB"] + my_stats["FantaAST"] + my_stats["FantaBLK"] + my_stats["FantaSTL"] + my_stats["FantaTOV"]
my_stats["ESPNFantasyTot"] = my_stats["FantasyPts"] * my_stats["GamesPlayed"]

# Normalization adjustments
my_stats["TmPtsNormRatio"] = filtered_df['Team_PerGame_PTS'] / PTS 
my_stats["TmAstNormRatio"] = filtered_df['Team_PerGame_AST'] / AST
my_stats["TmRebNormRatio"] = filtered_df['Team_PerGame_TRB'] / REB
my_stats["TmStlNormRatio"] = filtered_df['Team_PerGame_STL'] / STL
my_stats["TmBlkNormRatio"] = filtered_df['Team_PerGame_BLK'] / BLK

my_stats["PtsNorm"] = my_stats["PTS"] / my_stats["TmPtsNormRatio"] # Bug where earlier years become decimal
my_stats["AstNorm"] = my_stats["AST"] / my_stats["TmAstNormRatio"] 
my_stats["RebNorm"] = my_stats["REB"] / my_stats["TmRebNormRatio"] 
my_stats["StlNorm"] = my_stats["STL"] / my_stats["TmStlNormRatio"] 
my_stats["BlkNorm"] = my_stats["BLK"] / my_stats["TmBlkNormRatio"] 

my_stats = my_stats.round(3)

# Refilter the final df
#my_stats = my_stats[multi_filter(my_stats, ["PG","SG","SF","PF"], [1,1,1,1])].drop(index=0)
#my_stats = my_stats[multi_filter(my_stats, ["PG","SG","SF"], [1,1,1])].drop(index=0)
#my_stats = my_stats[multi_filter(my_stats, ["PG","SG",], [1,1])].drop(index=0)

my_stats.to_csv("mystats.csv")