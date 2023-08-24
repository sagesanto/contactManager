import json
import os
import time

import pandas as pd
import requests
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from queries import AllPeople, CreatePerson, ListByName, AllLists
from schemas import PersonSchema, ContactListModel, ContactList, personSchemaToModel, OutputPersonSchemaToModel
from starlette_graphene3 import parse
from csvInput import PHONE_NUMBER_DF_COLUMN, EMAIL_DF_COLUMN, CLASS_YEAR_DF_COLUMN, FIRST_NAME_DF_COLUMN, \
    LAST_NAME_DF_COLUMN, SCHOOL_DF_COLUMN, ROLE_DF_COLUMN
from schemas import OutputPersonSchema

endpoint = AIOHTTPTransport(url="http://127.0.0.1:8000/api")
client = Client(transport=endpoint, fetch_schema_from_transport=True)


def addContact(person: PersonSchema):
    personDict = person.model_dump(exclude_none=True, exclude_unset=True)
    result = client.execute(CreatePerson().query, variable_values=personDict)
    print("unparsed result:", result)
    result = CreatePerson.parse(result)
    print("parsed:", result)


def fetchAllContacts():
    result = client.execute(AllPeople().query)
    # print("unparsed result:", result)
    result = AllPeople.parse(result)
    # print("parsed:", result)
    # print("dict:", result.objects[0].asdict())
    return result.objects


def peopleOnList(listName):
    result = client.execute(ListByName().query, variable_values={'listName': listName})
    # print("unparsed result:", result)
    result = ListByName.parse(result)
    # for p in result.objects:
    #     print("dict:", p.asdict())
    return result.objects


def outPeopleToDf(people: list[OutputPersonSchema]):
    result = [p.asdict() for p in people]
    df = pd.DataFrame(result)
    sqlColumns = ["FirstName", "LastName", "Roles", "ContactLists", "PhoneNumber", "DateAdded", "DateLastEdited",
                  "Emails", "Years", "Schools"]
    outColumns = [FIRST_NAME_DF_COLUMN, LAST_NAME_DF_COLUMN, ROLE_DF_COLUMN, "Associated Lists", PHONE_NUMBER_DF_COLUMN,
                  "Date Added", "Date Last Edited",
                  EMAIL_DF_COLUMN, CLASS_YEAR_DF_COLUMN, SCHOOL_DF_COLUMN]
    columnMapping = dict(zip(sqlColumns, outColumns))
    df = df.rename(columns=columnMapping)
    # print(df)
    # df = obj_df.head(1).combine_first(obj_df.tail(1)).join(num_df.head(1).add(num_df.tail(1)))
    return df


def peopleToCsv(people, newFilename):
    df = outPeopleToDf(people)
    df.to_csv(newFilename)


def csvByList(listName, newFilename):
    peopleToCsv(peopleOnList(listName), newFilename)


def allListsToCsvs(dirPath):
    if not os.path.exists(dirPath):
        os.mkdir(dirPath)
    result = AllLists.parse(client.execute(AllLists().query)).objects[0]["allLists"]
    for r in result:
        csvByList(r["ListName"], dirPath + "/" + r["CsvFilePath"][:-4] + "_ENRICHED.csv")
        print(f"Output csv {dirPath + '/' + r['CsvFilePath'][:-4] + '_ENRICHED.csv'}")


if __name__ == "__main__":
    # p = PersonSchema.model_validate(
    #     {'FirstName': 'Vincent', 'LastName': 'Miller', 'PhoneNumber': '9307114963', 'ContactLists': [ContactList('DummyRandomData')],
    #      'Email': 'v.miller@randatmail.com', 'Role': 'vgondw', 'School': 'cszjte'}
    # )

    # addContact(p)
    # outPeopleToDf(fetchAllContacts())
    # peopleOnList("UnknownList")
    # csvsByList("UnknownList","out.csv")
    # fetchAllContacts()
    allListsToCsvs("enriched")
    peopleToCsv(fetchAllContacts(), "all.csv")

# print(f"Was able to complete {count} queries in 60 seconds.")
