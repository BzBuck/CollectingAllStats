import pandas as pd
import requests

csv_import = 'allscraped.csv'

# Read all of the data from a csv
# It should automatically convert types correctly
read_df = pd.read_csv(csv_import)

def req_filter(df, stat, min_value):
    df = df[df[stat] > min_value]
    return df

filtered_df = req_filter(read_df,"Minutes",1000)

filtered_df.to_csv("filtered.csv")
