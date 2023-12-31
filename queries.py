from abc import ABC, abstractmethod
from collections import namedtuple

from graphql_query import Operation, Query, Argument, Variable
from gql import Client, gql
from schemas import PersonSchema, OutputPersonSchema

ClassYear = Variable(name="ClassYear", type="Int")
Email = Variable(name="Email", type="String")
FirstName = Variable(name="FirstName", type="String!")
LastName = Variable(name="LastName", type="String")
PhoneNumber = Variable(name="PhoneNumber", type="String")
Role = Variable(name="Role", type="String")
School = Variable(name="School", type="String")
ContactList = Variable(name="ContactList", type="String!")

ListName = Variable(name="listName", type="String!")

# this is such a mess. don't know how this should be structured


allPeopleFields = ["FirstName", "LastName", "PhoneNumber", "DateAdded", "DateLastEdited",
                   "ContactLists {ListName, TableID, CsvFilePath, Date}",
                   "Emails {TableID, PersonID, Email}",
                   "Schools {TableID, School}",
                   "ClassYears {TableID, Year}",
                   "Roles {TableID, Role}"]


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


def cleanList(l):
    for i in l:
        if isinstance(i, list):
            i = cleanList(i)
        else:
            i = cleanDict(i)
    return l


def cleanDict(d):
    bad = []
    for k, v in d.items():
        if isinstance(v, list):
            d[k] = cleanList(v)
        else:
            if v is None:
                bad.append(k)
    for k in bad:
        del d[k]
    return d


class AllPeople(QueryBundle):
    @property
    def rawQuery(self):
        return Query(name="allPeople", fields=["FirstName", "LastName", "PhoneNumber", "DateAdded", "DateLastEdited",
                                               "ContactLists {ListName, TableID, CsvFilePath, Date}",
                                               "Emails {TableID, PersonID, Email}",
                                               "Schools {TableID, School}",
                                               "ClassYears {TableID, Year}",
                                               "Roles {TableID, Role}"])

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
                d = cleanDict(d)
                OutputPersonSchema.model_config['from_attributes'] = True
                p = OutputPersonSchema.model_validate(d)
                people.append(p)
            except Exception as e:
                print(f"Couldn't create schema from {d}: {repr(e)}")
                failed.append(d)
        return ret(people, failed)


allPeople = Operation(type="query", queries=[Query(name="allPeople", fields=["FirstName", "LastName"])])


class ListByName(QueryBundle):
    @property
    def rawQuery(self):
        return Query(name="listByName", arguments=[Argument(name="listName", value=ListName)],
                     fields=["ListName", "People {"+', '.join(allPeopleFields)+"}"])


    @property
    def operation(self):
        return Operation(type="query", variables=[ListName], queries=[self.rawQuery])

    @staticmethod
    def parse(result):
        # print(result['listByName'][0]["People"])
        return AllPeople.parse(dict({"People": result['listByName'][0]["People"]}))


class AllLists(QueryBundle):
    @property
    def rawQuery(self):
        return Query(name="allLists",
                     fields=["ListName", "CsvFilePath"])

    @property
    def operation(self):
        return Operation(type="query", queries=[self.rawQuery])
