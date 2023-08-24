# enable sqlalchemy and graphene to play nice
from typing import Optional

import pydantic_core.core_schema
from graphene_sqlalchemy import SQLAlchemyObjectType
from models import *
from pydantic import BaseModel, field_serializer


# Person: sqlAlchemy model; representation of record in Person table - models.py
# PersonModel: graphene representation of sqlAlchemy model - schemas.py
# PersonSchema: pydantic model to validate mutations (contact inserts) - schemas.py


# these models just correlate SQLAlchemy models to Graphene models, allowing
# GraphQL queries to easily interact with SQLAlchemy:
class PersonModel(SQLAlchemyObjectType):
    class Meta:
        model = Person


# not currently in use
# class NameAliasModel(SQLAlchemyObjectType):
#     class Meta:
#         model = NameAlias


class ClassYearModel(SQLAlchemyObjectType):
    class Meta:
        model = ClassYear


class ContactListModel(SQLAlchemyObjectType):
    class Meta:
        model = ContactList


class EmailModel(SQLAlchemyObjectType):
    class Meta:
        model = Email


class RoleModel(SQLAlchemyObjectType):
    class Meta:
        model = Role


class SchoolModel(SQLAlchemyObjectType):
    class Meta:
        model = School


pydanticPerson = sqlalchemy_to_pydantic(Person)
pydanticClassYear = sqlalchemy_to_pydantic(ClassYear)
pydanticContactList = sqlalchemy_to_pydantic(ContactList)
pydanticEmail = sqlalchemy_to_pydantic(Email)
pydanticRole = sqlalchemy_to_pydantic(Role)
pydanticSchool = sqlalchemy_to_pydantic(School)


# trying to make a schema that can construct person from sqlalchemy


# this pydantic schema will be used to validate incoming mutation requests
class PersonSchema(BaseModel):
    # model_config = dict(arbitrary_types_allowed=True)
    FirstName: str
    LastName: Optional[str] = None
    PhoneNumber: Optional[str] = None
    ClassYear: Optional[int] = None
    ContactList: str
    CsvFilePath: Optional[str] = None
    Email: Optional[str] = None
    Role: Optional[str] = None
    School: Optional[str] = None
    ID: Optional[int] = None
    DateAdded: Optional[str] = None
    DateLastEdited: Optional[str] = None


def personSchemaToModel(p: PersonSchema):
    return Person(ID=p.ID, FirstName=p.FirstName, LastName=p.LastName, PhoneNumber=p.PhoneNumber, DateAdded=p.DateAdded,
                  DateLastEdited=p.DateLastEdited)


class OutputPersonSchema(pydanticPerson):
    # model_config = dict(arbitrary_types_allowed=True)
    ClassYears: Optional[List[pydanticClassYear]] = []
    ContactLists: List[pydanticContactList] = []
    CsvFilePath: Optional[str] = None
    Emails: Optional[List[pydanticEmail]] = None
    Roles: Optional[List[pydanticRole]] = None
    Schools: Optional[List[pydanticSchool]] = None
    ID: Optional[int] = None
    PhoneNumber: Optional[str] = None

    @field_serializer('ContactLists', 'ClassYears', 'Emails', 'Roles', 'Schools')
    def serialize_dt(self, ls, _info):
        if ls:
            temp = []
            for i in ls:
                temp.append(str(i))
            if temp:
                return ", ".join(temp)
        return None
        # return [str(i) for i in ls]

    def asdict(self):
        return self.model_dump()


# broken do not use :(
def OutputPersonSchemaToModel(p: OutputPersonSchema):
    return Person(ID=p.ID, FirstName=p.FirstName, LastName=p.LastName, PhoneNumber=p.PhoneNumber, DateAdded=p.DateAdded,
                  DateLastEdited=p.DateLastEdited, ContactLists=p.ContactLists, Roles=p.Roles, Emails=p.Emails,
                  Schools=p.Schools)
