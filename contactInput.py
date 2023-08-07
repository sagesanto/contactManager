from collections import namedtuple
from datetime import datetime
from abc import ABC, abstractmethod
import sys, os, pandas as pd, numpy as np
import re
from operator import attrgetter
import sqlite3
import formatters

SCHOOL_EMAIL_DF_COLUMN = "School Email"
EMAIL_DF_COLUMN = "Email"
CLASS_YEAR_DF_COLUMN = "Class Year"
FIRST_NAME_DF_COLUMN = "First Name"
LAST_NAME_DF_COLUMN = "Last Name"
PHONE_NUMBER_DF_COLUMN = "Phone Number"
SCHOOL_DF_COLUMN = "School"
ROLE_DF_COLUMN = "Role"

defaultRows = [EMAIL_DF_COLUMN, CLASS_YEAR_DF_COLUMN, FIRST_NAME_DF_COLUMN,
               LAST_NAME_DF_COLUMN, PHONE_NUMBER_DF_COLUMN, SCHOOL_DF_COLUMN, ROLE_DF_COLUMN]


# DELETE from Email;
# DELETE from ContactList;
# DELETE from Person;
# DELETE from Role;
# DELETE from School;
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def queryToDicts(queryResults):
    """
    Convert SQLite query results to a list of dictionaries.
    :param queryResults: List of SQLite query row objects.
    :return: List of dictionaries representing query results.
    """
    dictionary = [dict(row) for row in queryResults if row]
    return [{k: v for k, v in a.items()} for a in dictionary if a]


def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


class ContactDatabaseConnection:
    def __init__(self, dbPath, dateString):
        self.connection = sqlite3.connect(dbPath)
        self.connection.row_factory = sqlite3.Row  # get row results in a nice form
        self.db = self.connection.cursor()
        self.dateString = dateString

    def insertAlias(self, personId, aliasValue, aliasTableName):
        # print("Update!", "ID:", personId, "alias:", aliasTableName, "value:", aliasValue)
        self.db.execute(f"""
            INSERT INTO {aliasTableName}
            VALUES (?, ?)
        """, (personId, aliasValue))

    def insertAliasIfNotExists(self, personId, aliasValue, aliasColumnName, aliasTableName):
        # check if the alias already exists for the person
        if aliasValue is not None and not pd.isna(aliasValue):
            self.db.execute(f"""
                SELECT {aliasColumnName}
                FROM {aliasTableName}
                WHERE ID = ? AND {aliasColumnName} = ?
            """, (personId, aliasValue))
            existingAlias = self.db.fetchone()

            if not existingAlias:
                # insert the new alias for the person
                self.insertAlias(personId, aliasValue, aliasTableName)
            return
        # print("Did not edit alias", aliasColumnName, "for person #" + str(personId),
        #       "because the provided value was None.")

    # TODO: what to do when we get back more than one record? right now we just ignore all but the first one
    def getPersonRecord(self, ID):
        self.db.execute("""
        SELECT * FROM Person WHERE ID = ?
        """, (ID,))
        result = self.db.fetchall()
        return queryToDicts(result)[0] if len(result) else None

    def addRecord(self, row, description):
        firstName = row[FIRST_NAME_DF_COLUMN]
        lastName = row[LAST_NAME_DF_COLUMN]
        email = row[EMAIL_DF_COLUMN]
        number = row[PHONE_NUMBER_DF_COLUMN]
        self.db = self.connection.cursor()

        if pd.isna(email) and pd.isna(number):
            print(bcolors.BOLD, bcolors.FAIL, "WARNING: Contact", firstName, lastName,
                  "skipped. Must have email or phone number.", bcolors.ENDC)
            return
        if not pd.isna(email):
            query = """
                SELECT p.ID
                FROM Person p
                INNER JOIN Email ea ON p.ID = ea.ID
                WHERE (ea.Email = ? OR p.PhoneNumber = ?)
                    AND (p.PhoneNumber IS NULL OR p.PhoneNumber = ? OR ? IS NULL)
                """
            self.db.execute(query, (email, number, number, number))

        else:
            query = """
                SELECT p.ID
                FROM Person p
                WHERE p.PhoneNumber = ?
                """
            self.db.execute(query, (number,))

        match = self.db.fetchall()  # are there one or more matches already in the db?

        if match:
            # ---- record exists, we need to update it ----
            ID = match[0][0]
            # if len(match) > 1:
            #     raise ValueError("Something is wrong. ID {} gets more than one result!".format(ID))  # uh oh
            personRecord = self.getPersonRecord(ID)
            if not personRecord:
                raise ValueError("No person with ID {} exists!".format(ID))
            # print("Existing contact:", firstName, lastName, "ID:", ID)

            if number != personRecord["PhoneNumber"]:  # yippee, we got a phone #
                self.db.execute("""
                UPDATE Person 
                SET PhoneNumber = ?
                WHERE ID = ?
                """, (number, ID))

            if pd.isna(firstName) and pd.isna(lastName):
                raise ValueError("Error with ID {}: Both names cannot be blank".format(ID))
            if pd.notna(firstName):
                self.db.execute("UPDATE Person SET FirstName = ? WHERE ID = ?", (firstName, ID))
            if pd.notna(lastName):
                self.db.execute("UPDATE Person SET LastName = ? WHERE ID = ?", (lastName, ID))
            print("Finished person",firstName,lastName)

        else:  # this is a new person
            self.db.execute("SELECT ID FROM Person ORDER BY ID DESC LIMIT 1")
            res = self.db.fetchone()
            ID = int(res[
                         0]) + 1 if res is not None else 0  # our indexing is just to increment each ID by one. real advanced stuff
            #  ----- no record exists, we need to make a new one -----
            print("New contact:", firstName, lastName, "ID:", ID)
            # add record, email, school, alias, role, etc
            self.db.execute("INSERT INTO Person Values (?,?,?,?,?,?)",
                            (ID, firstName, lastName, number, self.dateString, timestamp()))
            pass

        aGroup = namedtuple("AliasGroup", "dfColumn aliasColumnName aliasTableName")
        aliasGroups = [
            aGroup(EMAIL_DF_COLUMN, "Email", "Email"),
            aGroup(ROLE_DF_COLUMN, "Role", "Role"),
            aGroup(CLASS_YEAR_DF_COLUMN, "Year", "ClassYear"),
            aGroup(SCHOOL_DF_COLUMN, "School", "School")
        ]
        # add aliases (records for fields that may have more than one entry (email, school affiliation, etc))
        for group in aliasGroups:
            self.insertAliasIfNotExists(ID, row[group.dfColumn], group.aliasColumnName, group.aliasTableName)

        self.db.execute("INSERT INTO ContactList VALUES (?, ?, ?)", (ID, description, self.dateString))
        self.db.execute("UPDATE Person SET DateLastEdited = ? WHERE ID = ?", (timestamp(), ID))

        self.connection.commit()
        self.db.close()  # closing the db, not the connection

    def unfold(self):
        pass

    def query(self):
        pass


def formatDf(df, fmters):
    for f in fmters:
        if f.inputColName in df.columns:
            df[f.outColNames] = df.apply(lambda row: f.format(row[f.inputColName]), axis='columns',result_type='expand')
    return df


if __name__ == "__main__":
    path = 'contacts.db'
    date = timestamp()

    with open("./CSVs/manifest.txt", "r") as f:
        lines = [l.split(", ") for l in f.readlines() if not l.startswith("%")]

    contactDb = ContactDatabaseConnection(path, date)

    nameFormatter = formatters.NameFormatter("Name", [FIRST_NAME_DF_COLUMN, LAST_NAME_DF_COLUMN])
    numberFormatter = formatters.PhoneNumberFormatter(PHONE_NUMBER_DF_COLUMN, [PHONE_NUMBER_DF_COLUMN])

    fmters = [numberFormatter, nameFormatter]

    for file, description in lines:
        df = formatDf(pd.read_csv("./CSVs/" + file),fmters)
        for col in [EMAIL_DF_COLUMN, CLASS_YEAR_DF_COLUMN, FIRST_NAME_DF_COLUMN, LAST_NAME_DF_COLUMN,
                    PHONE_NUMBER_DF_COLUMN, SCHOOL_DF_COLUMN, ROLE_DF_COLUMN]:
            if col not in df.columns:
                raise ValueError("CSV must have column header '" + col + "'")
        try:
            datetime.strptime(date, "%Y-%m-%d %H:%M")
        except:
            raise ValueError("Malformed date string")
        for index, row in df.iterrows():
            # print("Would have added",row,description)
            contactDb.addRecord(row, description.replace('\n',''))

    contactDb.connection.close()
