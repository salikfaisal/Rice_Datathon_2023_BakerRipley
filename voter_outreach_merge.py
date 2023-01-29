import pandas as pd

# imports data on Voter IDs Registered in Harris County
voter_data = pd.read_csv("Harris_County_Voter_ID_Info.csv")

# imports textbanking data
textbanking_attempts_df = pd.read_csv("TextBankingAttempts.csv")
textbanking_contacts_df = pd.read_csv("TextBankingContacts.csv")

# retrieves the Voter IDs of responses of significance ("Yes", "Unsure") to different questions asked through text
voters_texted = textbanking_attempts_df[textbanking_attempts_df["Voter ID"] != "--"]["Voter ID"].unique().tolist()
planning_vote = textbanking_contacts_df[(textbanking_contacts_df["Question Sent"] == "Planning to vote?")
                                        & (textbanking_contacts_df["response to question"] == "Yes")]["Voter ID"].unique().tolist()
proper_id_yes = textbanking_contacts_df[(textbanking_contacts_df["Question Sent"] == "Do you have the proper ID to vote?") &
                                        (textbanking_contacts_df["response to question"] == "Yes")]["Voter ID"].unique().tolist()
proper_id_unsure = textbanking_contacts_df[(textbanking_contacts_df["Question Sent"] ==
                                           "Do you have the proper ID to vote?")
                                           & (textbanking_contacts_df["response to question"] == "Unsure")]["Voter ID"].unique().tolist()

# Initializes a list of each voter's response to a question through text. 1 means "Yes", 0.5 means "Unsure",
# and 0 includes responses "No" as well as if a voter was not asked the question
text_attempted = []
plan_to_vote = []
proper_id = []
num_of_messages_sent = []

for voter_message_attempt in voters_texted:
    voter_id = str(voter_message_attempt)
    text_attempted.append(1)
    # A series of if-statements used to determine how each voter's response (or lack of response) will be coded as
    mess_sent_to = textbanking_attempts_df[(textbanking_attempts_df["Voter ID"] == voter_id) & (textbanking_attempts_df["message_direction"] == 'outgoing')]['Voter ID'].count()
    num_of_messages_sent.append(mess_sent_to)
    if voter_id in planning_vote:
        plan_to_vote.append(1)
        if voter_id in proper_id_yes:
            proper_id.append(1)
        elif voter_id in proper_id_unsure:
            proper_id.append(0.5)
        else:
            proper_id.append(0)
    else:
        plan_to_vote.append(0)
        proper_id.append(0)

# Creates a new dataframe for texting data
textbanking_df = pd.DataFrame({'Voter ID': voters_texted, 'Num_of_Messages_Sent_To': num_of_messages_sent,'Messaged': text_attempted, 'Plan_to_Vote': plan_to_vote,
                               'Has_Proper_ID': proper_id})

# converts list of Voter IDs to Numeric form
textbanking_df['Voter ID'] = textbanking_df['Voter ID'].astype(float)

# merge textbanking data
voter_data = voter_data.merge(textbanking_df, how='left')

print("Textbanking Data Added")
#
# imports Blockwalking Data
canvass_attempts = pd.read_csv("CanvassAttempts.csv")
canvass_successes = pd.read_csv("CanvassSuccesses.csv")

# merge canvassing data
voter_data = voter_data.merge(canvass_attempts, how='left')
voter_data = voter_data.merge(canvass_successes, how='left')
print("Blockwalking Data Added")

# import mailing data
mailed_data = pd.read_csv("MailerSent.csv")

# merge mailing data
voter_data = voter_data.merge(mailed_data, how='left')
print('Mailing Data Added')

# import phonebanking data
calls_attempted = pd.read_csv("CallsAttempted.csv")
calls_succeeded = pd.read_csv("CallsAnswered.csv")

# removes '--' from phonebanking data
calls_attempted = calls_attempted[calls_attempted['Voter ID'] != '--']
calls_succeeded = calls_succeeded[calls_succeeded['Voter ID'] != '--']

# converts dataframes from str to float
calls_attempted['Voter ID'] = calls_attempted['Voter ID'].astype(float)
calls_succeeded['Voter ID'] = calls_succeeded['Voter ID'].astype(float)

# merge phonebanking data
voter_data = voter_data.merge(calls_attempted, how='left')
voter_data = voter_data.merge(calls_succeeded, how='left')
print("Phonebanking Data Added")

# rename column
voter_data = voter_data.rename(columns={"Provincial": 'Provisional'})

print(voter_data.columns)

# voter_data['Mailer Sent'] = voter_data['Mailer Sent'].fillna(0)
# voter_data['Canvass Attempts'] = voter_data['Canvass Attempts'].fillna(0)
# voter_data['Num_of_Messages_Sent_To'] = voter_data['Num_of_Messages_Sent_To'].fillna(0)
# voter_data['Calls Attempted'] = voter_data['Calls Attempted'].fillna(0)

voter_data['Mail_Cost'] = 0.37 * voter_data['Mailer Sent']
voter_data['Canvass_Cost'] = 2 * voter_data['Canvass Attempts']
voter_data['Text_Cost'] = 0.06 * voter_data['Num_of_Messages_Sent_To']
voter_data['Call_Cost'] = 0.13 * voter_data['Calls Attempted']
voter_data['Total_Campaign_Cost'] = voter_data['Mail_Cost'] + voter_data['Canvass_Cost'] + voter_data['Text_Cost'] + voter_data['Call_Cost']

# export to csv
voter_data.to_csv("Complete_Voter_Data.csv", index=False, header=True)