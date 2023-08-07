from collections import namedtuple
from datetime import datetime
from abc import ABC, abstractmethod
import sys, os, pandas as pd, numpy as np
import re
from operator import attrgetter
import sqlite3
import formatters
from contactInput import queryToDicts
from contactInput import PHONE_NUMBER_DF_COLUMN, EMAIL_DF_COLUMN, CLASS_YEAR_DF_COLUMN, FIRST_NAME_DF_COLUMN, \
    LAST_NAME_DF_COLUMN, SCHOOL_DF_COLUMN, ROLE_DF_COLUMN


class DbConnection:
    def __init__(self, dbPath):
        self.connection = sqlite3.connect(dbPath)
        self.connection.row_factory = sqlite3.Row  # get row results in a nice form
        self.cursor = self.connection.cursor()


def sqlOutToDf(fetchAllResult):
    result = queryToDicts(fetchAllResult)
    df = pd.DataFrame(result)
    # df['Year'] = df['Year'].fillna(0)
    oldDf = df.copy()
    df['Year'] = df['Year'].fillna(0).astype(int).astype('str').str.rstrip('.0')
    df["PhoneNumber"] = df["PhoneNumber"].astype('str').str.rstrip('.0')
    df = df.groupby('ID').agg({
        'FirstName': 'first',
        'LastName': 'first',
        'PhoneNumber': 'first',
        'Year': lambda x: ", ".join(map(str, set(v for v in x if v != '0' and v))),  # Collect non-zero values in a list
        'ListName': lambda x: ", ".join(map(str, set(x.tolist()))),
        'School': lambda x: ", ".join(map(str, set(x.tolist()))),
        'Role': lambda x: ", ".join(map(str, set(x.tolist()))),
        'Email': lambda x: ", ".join(map(str, set(x.tolist()))),
        'First': 'first',
        'Last': 'first',
        'DateAdded': 'first',
        'DateLastEdited': 'first'
    }).reset_index()

    sqlColumns = ["FirstName", "LastName", "Role", "ListName", "PhoneNumber", "DateAdded", "DateLastEdited", "Email",
                  "First", "Last", "Year", "School"]
    outColumns = [FIRST_NAME_DF_COLUMN, LAST_NAME_DF_COLUMN, ROLE_DF_COLUMN, "Associated Lists", PHONE_NUMBER_DF_COLUMN,
                  "Date Added", "Date Last Edited",
                  EMAIL_DF_COLUMN, "First Name Aliases", "Last Name Aliases", CLASS_YEAR_DF_COLUMN, SCHOOL_DF_COLUMN]
    columnMapping = dict(zip(sqlColumns, outColumns))
    df = df.rename(columns=columnMapping)
    # obj_df = df.select_dtypes(include=[np.object])
    # num_df = df.select_dtypes(exclude=[np.object])
    print(df)
    # df = obj_df.head(1).combine_first(obj_df.tail(1)).join(num_df.head(1).add(num_df.tail(1)))
    return df


def outputFromQuery(query, db):
    db.cursor.execute(query)
    r = db.cursor.fetchall()
    return sqlOutToDf(r)


def outputByLists(lists, db):
    dfs = {}
    for l in lists:
        query = """SELECT p.*, e.*, r.*, s.*, cl.*, cy.*, a.*
                    FROM Person p
                    LEFT JOIN Email e ON p.ID = e.ID
                    LEFT JOIN Role r ON p.ID = r.ID
                    LEFT JOIN School s ON p.ID = s.ID
                    LEFT JOIN ContactList cl ON p.ID = cl.ID
                    LEFT JOIN ClassYear cy ON p.ID = cy.ID
                    LEFT JOIN Alias a ON p.ID = a.ID
                    WHERE p.ID IN (
                        SELECT ID
                        FROM ContactList
                        WHERE ListName = ?
                    )
            """
        db.cursor.execute(query, (l,))
        dfs[l] = sqlOutToDf(db.cursor.fetchall())
    return dfs


def reconstructLists(db):
    l = queryToDicts(db.cursor.execute("SELECT DISTINCT ListName FROM ContactList"))
    lists = [list(d.values())[0] for d in queryToDicts(db.cursor.execute("SELECT DISTINCT ListName FROM ContactList"))]
    return outputByLists(lists, db)


def outputAll(db: DbConnection):
    query = """SELECT p.*, e.*, r.*, s.*, cl.*, cy.*, a.*
                    FROM Person p
                    LEFT JOIN Email e ON p.ID = e.ID
                    LEFT JOIN Role r ON p.ID = r.ID
                    LEFT JOIN School s ON p.ID = s.ID
                    LEFT JOIN ContactList cl ON p.ID = cl.ID
                    LEFT JOIN ClassYear cy ON p.ID = cy.ID
                    LEFT JOIN Alias a ON p.ID = a.ID
            """
    return outputFromQuery(query, db)


if __name__ == "__main__":
    dbPath = "contacts.db"
    db = DbConnection(dbPath)
    dfs = reconstructLists(db)
    print(dfs)
    for listName, listDf in dfs.items():
        listDf.to_csv("reconstruct/{}_enriched.csv".format(listName))

    # df = outputAll(db)
    # df.to_csv("out.csv")
