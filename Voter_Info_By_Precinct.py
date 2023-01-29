import pandas as pd

# imports individual voter information
harris_individual_voter_info = pd.read_csv("Complete_Voter_Data.csv")

# imports precinct race data
harris_precincts_race = pd.read_csv("VTDs_22G_Pop.csv")

# drops columns that will not be used
harris_precincts_race = harris_precincts_race.drop(['CountyFIPS', 'County', 'CNTYVTD', 'nanglo', 'bh', 'nanglovap', 'bhvap'], axis=1)

# drops precincts with 0 total people from race data
harris_precincts_race = harris_precincts_race[harris_precincts_race['total'] > 0]

harris_precincts_race['AngloVAPPerc'] = harris_precincts_race['anglovap'] / harris_precincts_race['vap']
harris_precincts_race['HispVAPPerc'] = harris_precincts_race['hispvap'] / harris_precincts_race['vap']
harris_precincts_race['BlackVAPPerc'] = harris_precincts_race['blackvap'] / harris_precincts_race['vap']
harris_precincts_race['AsianVAPPerc'] = harris_precincts_race['asianvap'] / harris_precincts_race['vap']

# renames "VTD" column to "Precinct"
harris_precincts_race = harris_precincts_race.rename(columns={'VTD': 'Precinct'})

# replaces a precinct such as '0675A' with '0675'
def replace_precinct_letter(row):
    if 'A' in row['Precinct']:
        row['Precinct'] = row['Precinct'][0:-1]
    return row
harris_precincts_race = harris_precincts_race.apply(replace_precinct_letter, axis='columns')

# changes precincts in demographic data to float
harris_precincts_race['Precinct'] = harris_precincts_race['Precinct'].astype(float)

# summarizes data for each precinct by columns with numerical values
precinct_level_data = harris_individual_voter_info.groupby('Precinct').sum(numeric_only=True)
median_age = harris_individual_voter_info.groupby('Precinct')['Age'].median()
precinct_level_data = precinct_level_data.rename(columns={'Age': 'Median_Age'})
precinct_level_data['Median_Age'] = median_age

# drops columns where summary of numerical data does not apply
precinct_level_data = precinct_level_data.drop(['Voter ID', 'Zip'], axis=1)
precinct_level_data = precinct_level_data.reset_index()

# merges racial demographics with precinct level data
precinct_level_data = precinct_level_data.merge(harris_precincts_race, how='left')

# finds the voter turnout for each precinct
precinct_level_data['Voter_Turnout_Rate'] = precinct_level_data['Voting Status'] / precinct_level_data['vap']
precinct_level_data = precinct_level_data[precinct_level_data['Voter_Turnout_Rate'] < 1]

# exports data to csv
precinct_level_data.to_csv("Precinct_Level_Data_Summary.csv", index=False, header=True)