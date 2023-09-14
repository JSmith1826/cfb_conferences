### Sports Referefence Historical Football Scores Scaper
## Scrapes all available college football scores from Sports Reference.com 
## by looping through the full season schedule for each year in the range specified.
## The script also does some light data transformation before saving the data to a CSV file.

# Dependencies
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np

import time
import random



# URL of page to be scraped
BASE_URL ='https://www.sports-reference.com/cfb/years/'
END_URL = '-schedule.html'



# min_dealy = 3 # site terms stay they kick if request >20 per minute

# https://www.sports-reference.com/cfb/years/1988-schedule.html

### FUNCTIONS

def scrape_year_data(year):
    """Scrape game data for a given year from sports-reference.com."""
    # Construct URL for the given year
    url = BASE_URL + str(year) + END_URL
    
    # Try reading the table into a pandas DataFrame
    try:
        df = pd.read_html(url)
        df = pd.DataFrame(df[0])  # Convert response from list to dataframe
    except:
        return None  # Return None if scraping fails
    
    # Clean the dataframe of rows that are not games
    df = df[df['Wk'] != 'Wk']
    
    # Add a 'Year' column to the dataframe to keep track of the year
    df['Year'] = year
    
    return df



def scrape_all_years(start_year, end_year):
    """Scrape game data for all years in the given range."""
    
    # Initialize an empty master dataframe
    master_df = pd.DataFrame()
    
    for year in range(start_year, end_year + 1):
        # Scrape data for the current year
        year_data = scrape_year_data(year)
        
        if year_data is not None:
            # Append the data to the master dataframe
            master_df = master_df.append(year_data, ignore_index=True)
        
        # Save to CSV every 10 years as a backup
        if year % 10 == 0:
            master_df.to_csv(f"TEMP\data_backup_{year}.csv", index=False)
        
        # Sleep for 3 seconds to respect rate limits
        time.sleep(3.5)
    
    # Save the entire data at the end
    master_df.to_csv("all_years_data.csv", index=False)
    
    return master_df

### DATA TRANFORMATION
# Dictionary to store unique IDs for schools
school_id_dict = {}


# Reorder the columns to match the desired configuration
ordered_cols = ['HostSchoolId', 'HostScore', 'HostTeamName', 'AwaySchoolId', 'AwayScore', 
                'AwayTeamName', 'ContestNotes', 'HostResult', 'AwayResult', 'Wk', 
                'Date', 'Day', 'Winner', 'Pts', 'Loser', 'Pts.1', 'Notes', 'Year']


# Function to generate unique IDs for school names
def generate_school_id(name, school_id_dict):
    if name not in school_id_dict:
        school_id_dict[name] = len(school_id_dict) + 1
    return school_id_dict[name]

def transform_data_neutral(row, school_id_dict):
    # Check if the game is a neutral site game
    if row['Unnamed: 6'] == 'N' or (pd.notnull(row['Unnamed: 6']) and row['Unnamed: 6'] != '@'):
        row['HostTeamName'] = row['Winner']
        row['HostScore'] = row['Pts']
        row['AwayTeamName'] = row['Loser']
        row['AwayScore'] = row['Pts.1']
        row['HostResult'] = 'Neutral'
        row['AwayResult'] = 'Neutral'
    # Check if the winner was the away team
    elif row['Unnamed: 6'] == '@':
        row['HostTeamName'] = row['Loser']
        row['HostScore'] = row['Pts.1']
        row['AwayTeamName'] = row['Winner']
        row['AwayScore'] = row['Pts']
        row['HostResult'] = 'Loss'
        row['AwayResult'] = 'Win'
    else:
        row['HostTeamName'] = row['Winner']
        row['HostScore'] = row['Pts']
        row['AwayTeamName'] = row['Loser']
        row['AwayScore'] = row['Pts.1']
        row['HostResult'] = 'Win'
        row['AwayResult'] = 'Loss'
    
    # Generate unique IDs for schools
    row['HostSchoolId'] = generate_school_id(row['HostTeamName'], school_id_dict)
    row['AwaySchoolId'] = generate_school_id(row['AwayTeamName'], school_id_dict)
    
    row['ContestNotes'] = row['Notes']
    
    return row








## intialize the scrape
# Set the start and end years
data = scrape_all_years(186*, 1899) # 1869 is the first year of college football




# Apply the transformations to each row of the dataframe with neutral site games handling
transformed_data = data.apply(lambda row: transform_data_neutral(row, school_id_dict), axis=1)

# Drop the 'Rk' and 'Unnamed: 6' columns
transformed_data = transformed_data.drop(columns=['Rk', 'Unnamed: 6'])

# Reorder the columns to match the desired configuration
transformed_data = transformed_data[ordered_cols]
transformed_data.head(20)


# Save to A CSV File
transformed_data.to_csv("../TEMP/cfb_scores_all_years.csv", index=False) # Save to TEMP Directory for inspection
# transformed_data.to_csv("../data/cfb_scores_all_years.csv", index=False) # Save to data Directory - production