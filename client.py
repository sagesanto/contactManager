import json
import time

import requests
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from queries import AllPeople, CreatePerson
from schemas import PersonSchema, ContactListModel, ContactList, personSchemaToModel
from starlette_graphene3 import parse

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
    print("unparsed result:", result)
    result = AllPeople.parse(result)
    print("parsed:", result)
    back = personSchemaToModel(result.objects[0])
    print("Back to person:", back)


if __name__ == "__main__":
    # p = PersonSchema.model_validate(
    #     {'FirstName': 'Vincent', 'LastName': 'Miller', 'PhoneNumber': '9307114963', 'ContactLists': [ContactList('DummyRandomData')],
    #      'Email': 'v.miller@randatmail.com', 'Role': 'vgondw', 'School': 'cszjte'}
    # )

    # addContact(p)

    fetchAllContacts()

# print(f"Was able to complete {count} queries in 60 seconds.")
