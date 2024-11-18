import requests
import pandas as pd
import numpy as np
import json
from bs4 import BeautifulSoup, Comment
from unidecode import unidecode

year = 2024
season = f"{year - 1}-{year % 100:02}" 

url = f"https://www.basketball-reference.com/leagues/NBA_{year}.html"

def request_data(url):
    response = requests.get(url)
    data = response.text
    return data

def get_soup(year):
    url = f"https://www.basketball-reference.com/leagues/NBA_{year}.html"
    html_content = request_data(url)

    soup = BeautifulSoup(html_content, 'html.parser')

    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        if "data" in comment:
            comment.replace_with(BeautifulSoup(comment, 'html.parser'))

    return soup


def get_table(year):
    soup = get_soup(year)
    tables = soup.find_all("table")
    dfs = []
    table_types = ["PerGame","OppPerGame","Tot","OppTot","Per100","OppPer100","Adv","Shooting","OppShooting"]
    team_codes = [["League Average","TOT"],
    ["Atlanta Hawks", "ATL"],
    ["Boston Celtics", "BOS"],
    ["Brooklyn Nets", "BKN"],
    ["Charlotte Hornets", "CHA"],
    ["Chicago Bulls", "CHI"],
    ["Cleveland Cavaliers", "CLE"],
    ["Detroit Pistons", "DET"],
    ["Indiana Pacers", "IND"],
    ["Miami Heat", "MIA"],
    ["Milwaukee Bucks", "MIL"],
    ["New York Knicks", "NYK"],
    ["Orlando Magic", "ORL"],
    ["Philadelphia 76ers", "PHI"],
    ["Toronto Raptors", "TOR"],
    ["Washington Wizards", "WAS"],
    ["Dallas Mavericks", "DAL"],
    ["Denver Nuggets", "DEN"],
    ["Golden State Warriors", "GSW"],
    ["Houston Rockets", "HOU"],
    ["Los Angeles Clippers", "LAC"],
    ["Los Angeles Lakers", "LAL"],
    ["Memphis Grizzlies", "MEM"],
    ["Minnesota Timberwolves", "MIN"],
    ["New Orleans Pelicans", "NOP"],
    ["Oklahoma City Thunder", "OKC"],
    ["Phoenix Suns", "PHX"],
    ["Portland Trail Blazers", "POR"],
    ["Sacramento Kings", "SAC"],
    ["San Antonio Spurs", "SAS"],
    ["Utah Jazz", "UTA"],
    ["Charlotte Bobcats", "CHA"],
    ["New Jersey Nets", "NJN"],
    ["New Orleans Hornets", "NOH"]]
    team_dict = {team[0]: team[1] for team in team_codes}
    
    
    for i in range(20, 29):
        table = tables[i]
        
        if not table:
            print(f"No table found at index {i}")
            continue

        headers = []
        for th in table.find_all("th", {"scope": "col"}):
            header_text = th.text.strip()
            over_header = th.get("data-over-header", "").strip()
            if header_text:
                if over_header:
                    head_string = f"Team_{table_types[i-20]}_{over_header}_{header_text}"
                    head_string = head_string.replace(' ', '')
                    headers.append(head_string)
                else:
                    header_text = f"Team_{table_types[i-20]}_{header_text}"
                    headers.append(header_text)

        # Extract rows
        tbody = table.find("tbody") or table  # Use `table` if `tbody` is None
        rows = []
        
        try:
            for tr in tbody.find_all("tr"):
                row = [td.text.strip().replace('*', '')  for td in tr.find_all("td") if td.text.strip() != '']
                if tr.find("th"):
                    row.insert(0, tr.find("th").text.strip())
                rows.append(row)
            
            df = pd.DataFrame(rows, columns=headers)
            df['Team'] = df[headers[1]]
            df["TeamAbbreviation"] = df['Team'].map(team_dict)
            dfs.append(df)
            
        except Exception as e:
            print(f"Error processing table at index {i}: {e}\n")
            continue
    
    
    
    
    return dfs

def merge_dfs_keep_first_cols(df1, df2, on_col):
    # Determine which columns are exclusively in df2
    non_overlap_cols = [col for col in df2.columns if col not in df1.columns or col == on_col]

    # Subset df2 to include only these non-overlapping columns
    df2_subset = df2[non_overlap_cols]

    # Merge df1 with the subset of df2
    merged_df = pd.merge(df1, df2_subset, on=on_col, how='left')

    return merged_df

def merge_all_tables(year):
    all_tables = get_table(year)
    my_table = all_tables[0]

    for i in range(1,len(all_tables)): # 9 default
        my_table = merge_dfs_keep_first_cols(my_table, all_tables[i],'Team')

    return my_table

my_table = merge_all_tables(year)
my_table.to_csv('tmtst.csv')
