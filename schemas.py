# enable sqlalchemy and graphene to play nice
from typing import Optional
from graphene_sqlalchemy import SQLAlchemyObjectType
from models import *
from pydantic import BaseModel


# Person: sqlAlchemy model; representation of record in Person table - models.py
# PersonModel: graphene representation of sqlAlchemy model - schemas.py
# PersonSchema: pydantic model to validate mutations (contact inserts) - schemas.py


# this pydantic schema will be used to validate incoming mutation requests

class PersonSchema(BaseModel):
    FirstName: str
    LastName: Optional[str] = None
    PhoneNumber: Optional[str] = None
    ClassYear: Optional[int] = None
    ContactList: str
    Email: Optional[str] = None
    Role: Optional[str] = None
    School: Optional[str] = None
    ID: Optional[int] = None
    DateAdded: Optional[str] = None
    DateLastEdited: Optional[str] = None


def personSchemaToModel(p: PersonSchema):
    return Person(ID=p.ID, FirstName=p.FirstName, LastName=p.LastName, PhoneNumber=p.PhoneNumber, DateAdded=p.DateAdded,
                  DateLastEdited=p.DateLastEdited)


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
