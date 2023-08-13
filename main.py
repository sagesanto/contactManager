from sqlalchemy.orm import joinedload, subqueryload

import dbConfig
from models import Person, ContactList
from sqlalchemy import func, asc, desc


def listByNumber(session, ascending=False):
    if not isinstance(ascending, bool):
        raise ValueError(f"Sorting value invalid: {ascending}")

    direction = asc if ascending else desc
    return (
        session.query(
            ContactList.ListName, func.count(Person.FirstName).label("numPeople")
        )
        .join(ContactList.Person)
        .group_by(ContactList.ListName)
        .order_by(direction("numPeople"))
    )


def peopleAndTheirLists(session):
    return (
        session.query(Person.FirstName, Person.LastName, func.group_concat(ContactList.ListName))
        .join(ContactList)
        .group_by(Person.ID)
        .order_by(Person.FirstName, Person.LastName)
    )


def orderPeopleByMostLists(session, ascending=False):
    if not isinstance(ascending, bool):
        raise ValueError(f"Sorting value invalid: {ascending}")

    direction = asc if ascending else desc

    return (
        session.query(
            Person.FirstName, func.count(ContactList.ListName).label("total_contact_lists")
        )
        .join(Person.ContactLists)
        .group_by(Person.ID)
        .order_by(direction("total_contact_lists"))
    )


dbSession = dbConfig.dbSession
# contact_lists = dbSession.query(ContactList).filter_by(ID=0).all()
# person = dbSession.query(Person).options(joinedload(Person.ContactLists)).filter_by(ID=0).all()
# contact_lists = person.ContactLists
contact_lists = dbSession.query(ContactList).options(subqueryload(ContactList.Person)).filter_by(PersonID=0).all()
print()
for contact_list in contact_lists:
    print(contact_list.PersonID, contact_list.ListName, contact_list.Date)
    if contact_list.Person:
        print("Associated Person:", contact_list.Person.FirstName, contact_list.Person.LastName, contact_list.Person.ID)
    else:
        print("No Associated Person")
# listByPerson = orderPeopleByMostLists(db)
#
# for row in listByPerson:
#     print(row)
#     print(f"Person: {row.FirstName}, Lists: {row.total_contact_lists}")
#
# # ls = listByNumber(db)
# ls = peopleAndTheirLists(db)
# for row in ls:
#     print(row)
