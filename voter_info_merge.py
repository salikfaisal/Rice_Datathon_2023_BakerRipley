import pandas as pd
import time
import math

# imports data on Harris County Registered Voters
harris_voters_1 = pd.read_csv("AllRegistered_Harris_1of3.csv")
harris_voters_2 = pd.read_csv("AllRegistered_Harris_2of3.csv")
harris_voters_3 = pd.read_csv("AllRegistered_Harris_3of3.csv")

# combines 3 dataframes into 1
harris_frames = [harris_voters_1, harris_voters_2, harris_voters_3]
harris_voters = pd.concat(harris_frames)

# removes suspended voters from consideration
harris_voters = harris_voters[harris_voters["Status"] != 'Suspense']

# imports data on voting in the 2022 election
actual_voters_1 = pd.read_csv("Nov2022_Voters_1of3.csv")
actual_voters_2 = pd.read_csv("Nov2022_Voters_2of3.csv")
actual_voters_3 = pd.read_csv("Nov2022_Voters_3of3.csv")

actual_voters = pd.concat([actual_voters_1, actual_voters_2, actual_voters_3])
actual_voters = actual_voters.reset_index()

# Only selects specific columns
actual_voters = actual_voters.filter(["Voter ID", "VOTE_TYPE", "BIRTHYEAR", "SEX", "Voting Site", "Voting Precinct"], axis=1)

# creates columns for each voting type
actual_voters["Voted_Election_Day"] = (actual_voters["VOTE_TYPE"] == 'E').astype(int)
actual_voters["Mail_In_Ballot"] = (actual_voters["VOTE_TYPE"].isin(['M', 'A'])).astype(int)
actual_voters["Early_In_Person"] = (actual_voters["VOTE_TYPE"] == 'P').astype(int)
actual_voters["Provincial"] = (actual_voters["VOTE_TYPE"] == 'Z').astype(int)

# Fix Data for one problematic row
actual_voters.at[1062757, 'BIRTHYEAR'] = 1998
actual_voters.at[1062757, 'SEX'] = 'NaN'
actual_voters.at[1062757, 'Voting Site'] = 'NaN'

# Calculates Age in 2022
num_voted = len(actual_voters['Voter ID'])
start_time = time.time()
ages_of_voters = []
voters_examined = 0

for row_num, row in actual_voters.iterrows():
    if row['BIRTHYEAR'] == 'NaN':
        ages_of_voters.append('NaN')
    elif type(row['BIRTHYEAR']) == str:
        ages_of_voters.append(2022 - int(row['BIRTHYEAR']))
    else:
        ages_of_voters.append(2022 - row['BIRTHYEAR'])
    if row_num % 10000 == 0:
        print((voters_examined + 1) / num_voted * 100, '% complete')
        end_time = time.time()
        time_so_far = (end_time - start_time) / 60
        time_when_finished = time_so_far / (voters_examined + 1) * num_voted
        print(time_when_finished - time_so_far, "minutes left")
    voters_examined += 1
actual_voters['AGE'] = ages_of_voters
actual_voters['Voting Status'] = 1

# we no longer need the 'Vote Type' Column or the 'BIRTHYEAR' column
actual_voters = actual_voters.drop(['VOTE_TYPE', 'BIRTHYEAR'], axis=1)

# merge actual voting data with harris voters
harris_voters = harris_voters.merge(actual_voters, how="left")

# eliminates duplicate columns
harris_voters['Sex'] = harris_voters['SEX']
harris_voters['Age'] = harris_voters['AGE']
harris_voters = harris_voters.drop(['SEX', 'AGE'], axis=1)

number_of_voters_in_harris_tx = len(harris_voters['Voter ID'])
start_time = time.time()
updated_precincts = []
for row_num, row in harris_voters.iterrows():
    registered_precinct = row['Precinct']
    election_precinct = row['Voting Precinct']
    if math.isnan(election_precinct):
        updated_precincts.append(registered_precinct)
    else:
        updated_precincts.append(election_precinct)
    # used to determine the time remaining for the indexing of all rows
    if row_num % 10000 == 0:
        print((row_num + 1) / number_of_voters_in_harris_tx * 100, '% complete')
        end_time = time.time()
        time_so_far = (end_time - start_time) / 60
        time_when_finished = time_so_far / (row_num + 1) * number_of_voters_in_harris_tx
        print(time_when_finished - time_so_far, "minutes left")

# drops the "Voting Precinct" column after using it to replace the "Precinct" data
harris_voters["Precinct"] = updated_precincts
harris_voters = harris_voters.drop(['Voting Precinct'], axis=1)

# imports data on targeted voters
targeted_voters = pd.read_csv("TargetVoters.csv")

# drops columns that won't be used and adds a value of 1 to each targeted voter
targeted_voters = targeted_voters.drop(['City', 'Zip5'], axis=1)
targeted_voters['Target Voter'] = 1

# merged the targeted voters data
harris_voters = harris_voters.merge(targeted_voters, how="left")

# function to change precinct number when conflicting to BakerRipley Data (Nov 2022 Election Cycle)

number_of_voters_in_harris_tx = len(harris_voters['Voter ID'])
start_time = time.time()
updated_precincts = []
for row_num, row in harris_voters.iterrows():
    registered_precinct = row['Precinct']
    gotv_precinct = row['PrecinctName']
    if math.isnan(gotv_precinct):
        updated_precincts.append(registered_precinct)
    else:
        updated_precincts.append(gotv_precinct)
    # used to determine the time remaining for the indexing of all rows
    if row_num % 10000 == 0:
        print((row_num + 1) / number_of_voters_in_harris_tx * 100, '% complete')
        end_time = time.time()
        time_so_far = (end_time - start_time) / 60
        time_when_finished = time_so_far / (row_num + 1) * number_of_voters_in_harris_tx
        print(time_when_finished - time_so_far, "minutes left")

# drops the "PrecinctName" column after using it to replace the "Precinct" data
harris_voters["Precinct"] = updated_precincts
harris_voters = harris_voters.drop(['PrecinctName'], axis=1)

print('Targeted Voters Added')



print(harris_voters.groupby('Precinct')['Target Voter'].count())

print(harris_voters.columns)
print(harris_voters)
print("November 2022 Voter Participation Data Added")
harris_voters.to_csv("Harris_County_Voter_ID_Info.csv", index=False, header=True)