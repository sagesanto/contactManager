from abc import ABC, abstractmethod
from collections import namedtuple

from graphql_query import Operation, Query, Argument, Variable
from gql import Client, gql
from schemas import PersonSchema

ClassYear = Variable(name="ClassYear", type="Int")
ContactList = Variable(name="ContactList", type="String!")
Email = Variable(name="Email", type="String")
FirstName = Variable(name="FirstName", type="String!")
LastName = Variable(name="LastName", type="String")
PhoneNumber = Variable(name="PhoneNumber", type="String")
Role = Variable(name="Role", type="String")
School = Variable(name="School", type="String")


# this is such a mess. don't know how this should be structured


class QueryBundle(ABC):
    @property
    def query(self):
        # this is the last assembly step - make a query usable with the client
        return gql(self.operation.render())

    @property
    @abstractmethod
    def rawQuery(self):
        # this initializes the actual Query object
        pass

    @property
    @abstractmethod
    def operation(self):
        # this is the Operation object that goes with the query
        pass

    @staticmethod
    def parse(result):
        # given the result of a successful query of this type, transform it into a useful form
        # this default just spits the input back out
        ret = namedtuple("Parsed", "objects failed")
        return ret([result], [])


class CreatePerson(QueryBundle):
    @property
    def rawQuery(self):
        return Query(
            name="addContact",
            arguments=[
                Argument(name="ClassYear", value=ClassYear),
                Argument(name="ContactList", value=ContactList),
                Argument(name="Email", value=Email),
                Argument(name="FirstName", value=FirstName),
                Argument(name="LastName", value=LastName),
                Argument(name="PhoneNumber", value=PhoneNumber),
                Argument(name="Role", value=Role),
                Argument(name="School", value=School)
            ],
            fields=["ok", "ID", "isNewContact"]
        )

    @property
    def operation(self):
        return Operation(type="mutation",
                         name="AddContact",
                         variables=[ClassYear, ContactList, Email, FirstName, LastName, PhoneNumber, Role,
                                    School],
                         queries=[self.rawQuery])


class AllPeople(QueryBundle):
    @property
    def rawQuery(self):
        return Query(name="allPeople", fields=["FirstName", "LastName", "PhoneNumber", "ContactLists {ListName}"])

    @property
    def operation(self):
        return Operation(type="query", queries=[self.rawQuery])

    @staticmethod
    def parse(result):
        ret = namedtuple("Parsed", "objects failed")
        people = []
        failed = []
        for d in list(result.values())[0]:
            try:
                p = PersonSchema.model_validate(d)
                people.append(p)
            except Exception as e:
                print(f"Couldn't create schema from {d}: {repr(e)}")
                failed.append(d)
        return ret(people, failed)


allPeople = Operation(type="query", queries=[Query(name="allPeople", fields=["FirstName", "LastName"])])
