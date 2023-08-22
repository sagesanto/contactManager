# Server - the meat of the program

import graphene
from fastapi import FastAPI
from starlette_graphene3 import GraphQLApp, make_graphiql_handler

import addContact
import models, schemas
from dbConfig import dbSession
from models import ContactList, Person
from sqlalchemy import func, asc, desc, and_, select
from sqlalchemy.orm import aliased, joinedload
from schemas import PersonSchema


class Query(graphene.ObjectType):
    allPeople = graphene.List(schemas.PersonModel)
    peopleOnList = graphene.List(schemas.PersonModel, listName=graphene.String(required=True))
    allLists = graphene.List(schemas.ContactListModel)

    @staticmethod
    def resolve_allPeople(self, info):
        query = schemas.PersonModel.get_query(info)
        print(str(query.statement))
        # print(query.compile())
        res = query.all()
        return res

    @staticmethod
    def resolve_peopleOnList(self, info, listName):
        return dbSession.query(Person).join(ContactList.People).filter(ContactList.ListName==listName).all()

    @staticmethod
    def resolve_allLists(self, info):
        cl1 = aliased(ContactList)

        subquery = (
            dbSession.query(cl1.ListName, func.min(cl1.ID).label('min_id'))
            .group_by(cl1.ListName)
            .subquery()
        )

        return (
            dbSession.query(ContactList)
            .join(subquery, and_(ContactList.ListName == subquery.c.ListName, ContactList.ID == subquery.c.min_id))
            .all()
        )


class AddContact(graphene.Mutation):
    class Arguments:
        FirstName = graphene.String(required=True)
        LastName = graphene.String()
        PhoneNumber = graphene.String()
        ClassYear = graphene.Int()
        ContactList = graphene.String(required=True)
        Email = graphene.String()
        Role = graphene.String()
        School = graphene.String()

    # return values
    ok = graphene.Boolean()
    ID = graphene.Int()
    isNewContact = graphene.Boolean()

    @staticmethod
    def mutate(root, info, FirstName, ContactList, LastName=None, PhoneNumber=None, ClassYear=None, Email=None, Role=None, School=None):
        print(locals())
        # validate their input
        person = PersonSchema(FirstName=FirstName, LastName=LastName, PhoneNumber=PhoneNumber, ClassYear=ClassYear,
                              ContactList=ContactList, Email=Email, Role=Role, School=School)
        print(person)
        ok, ID, isNewContact = addContact.addRecord(person)
        return AddContact(ok=ok, ID=ID, isNewContact=isNewContact)


class PersonMutations(graphene.ObjectType):
    addContact = AddContact.Field()


app = FastAPI()
app.add_route("/api", GraphQLApp(schema=graphene.Schema(query=Query, mutation=PersonMutations), on_get=make_graphiql_handler()))
