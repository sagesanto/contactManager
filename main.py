import sys, os, pandas as pd, numpy as np
from operator import attrgetter

SCHOOL_EMAIL_COLUMN = "School Email"
PERSONAL_EMAIL_COLUMN = "Personal Email"
CLASS_YEAR_COLUMN = "Class Year"
FIRST_NAME_COLUMN = "First Name"
LAST_NAME_COLUMN = "Last Name"
PHONE_NUMBER_COLUMN = "Phone Number"
SCHOOL_COLUMN = "School"
ROLE_COLUMN = "Role"


def cleanDf(df: pd.DataFrame):
    newContacts = pd.DataFrame(columns=list(df.columns))

    # this is all painfully redundant but i dont care. i promise im a better programmer than this

    df.drop_duplicates(inplace=True)

    # identify all the rows that share a phone number, choose only the row with the fewest NaN values
    numbers = df[PHONE_NUMBER_COLUMN].to_numpy().tolist()
    uniqueNumbers = {x for x in set(numbers) if x == x}  # eliminate NaN value
    for number in uniqueNumbers:
        subDf = df.loc[df[PHONE_NUMBER_COLUMN] == number]
        lens = {}
        for i in range(len(subDf.index)):
            notNaN = subDf.iloc[i].isna().sum().sum()
            lens[notNaN] = i
        newContacts.loc[len(newContacts.index)] = lens[min(lens.keys())]  # need to be merging lines instead of overwriting !

    # now, combine rows sharing same email
    for emailColumn in [SCHOOL_EMAIL_COLUMN, PERSONAL_EMAIL_COLUMN]:
        emails = df[emailColumn].to_numpy().tolist()
        uniqueEmails = {x for x in set(emails) if x == x}  # eliminate NaN value
        for email in uniqueEmails:
            subDf = df.loc[df[emailColumn] == email]
            lens = {}
            for i in range(len(subDf.index)):
                notNaN = subDf.iloc[i].isna().sum().sum()
                lens[notNaN] = i
            newContacts.loc[len(newContacts.index)] = subDf.iloc[lens[min(lens.keys())]]

    # we may have added some rows twice by now. eliminate duplicates:
    newContacts.drop_duplicates(inplace=True)
    return newContacts


def mergeRecords(r1, r2):
    newer = max([r1,r2], key=attrgetter("addedEpoch"))
    # these two records are the same person. merge them, preferentially saving the newer info if conflict

    pass




# two people with the same email are the same person. store aliases.
# emails that contain "pitzer","pomona","hmc","scripps","cmc??" AND ".edu" are school emails. others are not
# when two instances of the same name appear, one associated with a school email and one with a personal email, assume same person
# phone numbers are unique identifiers. two people with the same phone number are the same person
# when a line is merged, the older origin date is kept

class ContactList:
    def __init__(self, csvPath, description = None):
        self.description = description or csvPath.split(os.sep)[-1][:-4]
        self.csvPath = csvPath
        self.df = cleanDf(pd.read_csv(csvPath))

    def mergeWith(self, ls):
        # group rows by person
        # to do this, group by name, then by phone number, then by email, then by expansive name search (maybe repeat this until we get zero hits?)
        # resolve each group
        # two people with the same email are the same person. store aliases.
        # emails that contain "pitzer","pomona","hmc","scripps","cmc??" AND ".edu" are school emails. others are not
        # when two instances of the same name appear, one associated with a school email and one with a personal email, assume same person
        # phone numbers are unique identifiers. two people with the same phone number are the same person
        # when a line is merged, the older origin date is kept

        # merge each line. we're the master list, the other list is the new one.
        otherDf = ls.df
        subDf = self.df[otherDf.columns]

        groups = {}  # name: list
        aliases = {} # alias: base name




