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


db = dbConfig.dbSession
listByPerson = orderPeopleByMostLists(db)

for row in listByPerson:
    print(row)
    print(f"Person: {row.FirstName}, Lists: {row.total_contact_lists}")

# ls = listByNumber(db)
ls = peopleAndTheirLists(db)
for row in ls:
    print(row)
