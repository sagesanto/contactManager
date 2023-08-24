import logging
import os
import sqlite3
from collections import namedtuple
from datetime import datetime
import pandas as pd, numpy as np
import sqlalchemy.exc

import schemas
import dbConfig
from models import Person, Email, Role, ClassYear, School, ContactList, PersonContactListAssociation, \
    PersonSchoolAssociation, PersonYearAssociation, PersonRoleAssociation, PersonEmailAssociation
from sqlalchemy.orm import aliased
from sqlalchemy import insert, and_, or_
from line_profiler_pycharm import profile

import cProfile
import io
import pstats
import contextlib

dateFormat = '%m/%d/%Y %H:%M:%S'
fileFormatter = logging.Formatter(fmt='%(asctime)s %(levelname)-2s | %(message)s', datefmt=dateFormat)
fileHandler = logging.FileHandler(os.path.abspath("./contacts.log"))
fileHandler.setFormatter(fileFormatter)
fileHandler.setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(fileHandler)
logger.setLevel(logging.INFO)


@contextlib.contextmanager
def profiled():
    pr = cProfile.Profile()
    pr.enable()
    yield
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
    ps.print_stats()
    # uncomment this to see who's calling what
    # ps.print_callers()
    print(s.getvalue())


class tcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


@profile
def IDIsOnList(dbSession, listName, ID):
    query = (
        dbSession.query(ContactList).filter((ContactList.ListName == listName) & (ContactList.PersonID == ID))
    )
    res = query.first()
    return res is not None


def findExistingListID(db, listName: str):
    r = db.query(ContactList).filter(ContactList.ListName == listName).first()
    return r.TableID if r else None


def ListAssociationExists(dbSession, personID, contactListID):
    query = (
        dbSession.query(PersonContactListAssociation)
        .filter(
            (PersonContactListAssociation.c.PersonID == personID) &
            (PersonContactListAssociation.c.ContactListID == contactListID)
        )
    )
    res = query.first()
    return res is not None


def mergeContacts(dbSession, id1, id2):
    if id1 == id2:
        return
    # make a contact with the superset of the information in contacts with ids id1 and id2, deferring to the contact with id id1
    # delete contact 2, edit contact 1
    # deleting contact 2 means pointing all associations with contact 2 to contact 1!
    person1 = getPersonRecord(dbSession, id1)
    person2 = getPersonRecord(dbSession, id2)
    logger.info(
        f"Attempting to merge person {id1} ({person1.FirstName} {person1.LastName}) with person {id2} ({person2.FirstName} {person2.LastName}).")
    p2PhoneNumber = person2.PhoneNumber

    toRemove = []
    #  merge the two relationships
    for obj_type, relationship in [(Email, "Emails"), (Role, "Roles"), (ClassYear, "ClassYears"), (School, "Schools")]:
        attrib = getattr(person2, relationship)
        i = 0
        while i < (len(attrib)):
            obj = attrib[i]
            if obj not in getattr(person1, relationship):
                getattr(person1, relationship).append(
                    obj)  # appending to this relationship will remove from the attrib list automatically
                logger.info(f"\tAdded {obj} to the first person's {relationship} relationship")
                obj.Person = person1
                obj.PersonID = id1
            else:
                i += 1
                # getattr(person2,relationship).remove(obj)
                # dbSession.delete(obj)
                # toRemove.append((relationship, obj))
    # for relationship, obj in toRemove:
    #     getattr(person2, relationship).remove(obj)

    for ls in person2.ContactLists:
        ls.People.remove(person2)
        logger.info(f"Removed person {id2} ({person2.FirstName} {person2.LastName}) from list {ls.ListName}.")
        if person1 not in ls.People:
            ls.People.append(person1)
            logger.info(f"Added person {id1} ({person1.FirstName} {person1.LastName}) to list {ls.ListName}.")

    dbSession.commit()
    dbSession.delete(person2)
    logger.info(f"Deleted person {id2}.")
    dbSession.commit()
    if person1.PhoneNumber is None:
        person1.PhoneNumber = p2PhoneNumber
    dbSession.commit()
    dbSession.close()


## different style of query (doesnt quite work but i like the vibe):
# p1 = aliased(Person)  # Alias for row Email is in person.Emails
# p2 = aliased(Person)  # Alias for row PhoneNumber = person.PhoneNumber AND person.PhoneNumber is not None
# p3 = aliased(Person)  # Alias for row PhoneNumber is None OR (row PhoneNumber = person.PhoneNumber AND person.PhoneNumber is not None) OR person.PhoneNumber is None
#
# # Constructing the query
# query = session.query(Person).\
#     join(p1, Person.Emails).filter(p1.Email == person.Email).\
#     join(p2, and_(Person.PhoneNumber == person.PhoneNumber, person.PhoneNumber.isnot(None))).\
#     join(p3, or_(Person.PhoneNumber.is_(None), Person.PhoneNumber == person.PhoneNumber, person.PhoneNumber.is_(None)))
#
# result = query.all()

@profile
def findExistingContactID(db, personSchema):
    p = aliased(Person)
    # a row matches if it meets the following:
    # row.Email == person.Email OR (row.PhoneNumber = person.PhoneNumber AND person.PhoneNumber is not None)
    # AND
    # row.PhoneNumber is None  OR (row.PhoneNumber = person.PhoneNumber AND person.PhoneNumber is not None) OR person.PhoneNumber is None
    if personSchema.Email:
        # Constructing the query
        query = db.query(p.ID). \
            filter(or_(
            and_(
                p.Emails.any(Email.Email == personSchema.Email),
                p.PhoneNumber == personSchema.PhoneNumber,
            ),
            or_(
                p.PhoneNumber is None,
                and_(
                    p.PhoneNumber == personSchema.PhoneNumber,
                    personSchema.PhoneNumber is not None
                ),
                personSchema.PhoneNumber is None
            ),
            and_(
                p.PhoneNumber == personSchema.PhoneNumber,
                personSchema.PhoneNumber is not None
            )
        ))

    elif personSchema.PhoneNumber:
        query = (
            db.query(p.ID)
            .filter(p.PhoneNumber == personSchema.PhoneNumber)
        )

    res = query.all()
    ID = None
    if not res and personSchema.PhoneNumber:
        query = (
            db.query(p.ID)
            .filter(p.PhoneNumber == personSchema.PhoneNumber)
        )
        res = query.all()
    if res:
        ID = res[0][0]
        if len(res) > 1:
            id1, id2 = res[0][0], res[1][0]
            if id1 != id2:
                mergeContacts(db, id1, id2)
                dbConfig.renewDbSession()
            # need to do a merge here
            # database commit?? have we started a transaction by this point
            print("Uh oh. multiple results")
    return bool(res), ID


@profile
def getPersonRecord(dbSession, ID):
    people = dbSession.query(Person).filter(Person.ID == ID).all()
    person = people[0]
    return person


# this function uses 'alias/Alias' to mean any new value/column/class for a table that is allowed
# to store multiple fields for each person. this includes the name
# this can be a little confusing:

def insertAlias(dbSession, personId, aliasValue, aliasModelClass, aliasColumnName):
    # print("Update!", "ID:", personId, "alias:", aliasTableName, "value:", aliasValue)
    newAlias = aliasModelClass(PersonID=personId)
    setattr(newAlias, aliasColumnName, aliasValue)
    dbSession.add(newAlias)
    dbSession.commit()


@profile
def insertAssociatedAlias(dbSession, personId, aliasValue, aliasModelClass, aliasColumnName, associationClass):
    # print("Update!", "ID:", personId, "alias:", aliasTableName, "value:", aliasValue)

    entryId = None
    filterCondition = {aliasColumnName: aliasValue}
    entryId = dbSession.query(aliasModelClass.TableID).filter_by(**filterCondition).first()

    if not entryId:
        newEntry = aliasModelClass()
        setattr(newEntry, aliasColumnName, aliasValue)
        dbSession.add(newEntry)
        dbSession.commit()
        entryId = newEntry.TableID
    else:
        entryId = entryId[0]

    statement = insert(associationClass).values(
        PersonID=personId,
        AssocID=entryId
    )
    try:
        dbSession.execute(statement)
    except sqlalchemy.exc.IntegrityError as e:
        print(e)
        pass

    dbSession.commit()


@profile
def insertAliasIfNotExists(dbSession, personId, aliasValue, aliasColumnName, aliasModelClass, associationClass=None):
    # check if the alias already exists for the person
    if aliasValue is not None and not pd.isna(aliasValue):
        # existingAlias = (
        #     dbSession.query(getattr(aliasModelClass, aliasColumnName))
        #     .filter(getattr(aliasModelClass, 'PersonID') == personId,
        #             getattr(aliasModelClass, aliasColumnName) == aliasValue)
        #     .first()
        # )

        # if not existingAlias:
        #     # insert the new alias for the person
        #     # with profiled():
        if associationClass is not None:
            insertAssociatedAlias(dbSession, personId, aliasValue, aliasModelClass, aliasColumnName, associationClass)
        else:
            insertAlias(dbSession, personId, aliasValue, aliasModelClass, aliasColumnName)

    return aliasValue is not None and not pd.isna(aliasValue)
    # print("DID not edit alias", aliasColumnName, "for person #" + str(personId),
    #       "because the provIDed value was None.")


@profile
def addRecord(person: schemas.PersonSchema):
    dbSession = dbConfig.dbSession

    edited = False
    if pd.isna(person.Email) and pd.isna(person.PhoneNumber):
        logger.warning(
            f"Contact {person.FirstName} {person.LastName} skipped. Must have Email or phone number.")
        return False, -1, False

    match, ID = findExistingContactID(dbSession, person)  # are there one or more matches already in the db?
    new = False
    if match:
        # ---- record exists, we need to update it ----
        # if len(match) > 1:
        #     raise ValueError("Something is wrong. ID {} gets more than one result!".format(ID))  # uh oh
        person.ID = ID
        personRecord = getPersonRecord(dbSession, ID)

        if not personRecord:
            raise ValueError("Internal error: no person with ID {} exists!".format(ID))
        # print("Existing contact:", FirstName, LastName, "ID:", ID)

        if str(person.PhoneNumber) != str(personRecord.PhoneNumber):  # yippee, we got a phone #
            logger.info(f"Updating phone number for {person.FirstName} {person.LastName}")
            dbSession.query(Person).filter_by(ID=ID).update({"PhoneNumber": person.PhoneNumber})

        if person.FirstName and person.FirstName != personRecord.FirstName:
            personRecord.FirstName = person.FirstName
            edited = True
        if person.LastName and person.LastName != personRecord.LastName:
            personRecord.LastName = person.LastName
            edited = True

    else:  # this is a new person
        new = True
        if not person.FirstName and not person.LastName:
            raise ValueError("Error with ID {}: Both names cannot be blank when inserting contact.".format(ID))
        latestId = dbSession.query(Person.ID).order_by(Person.ID.desc()).limit(1).scalar()
        ID = int(
            latestId) + 1 if latestId is not None else 0  # our indexing is just to increment each ID by one. real advanced stuff
        #  ----- no record exists, we need to make a new one -----
        logger.info(f"New contact: {person.FirstName} {person.LastName} ID: {ID}")
        # add record, Email, School, alias, Role, etc
        person.ID = ID
        person.DateAdded, person.DateLastEdited = timestamp(), timestamp()
        newPerson = schemas.personSchemaToModel(person)

        dbSession.add(newPerson)

    dbSession.commit()

    aGroup = namedtuple("AliasGroup", "aliasValue aliasColumnName aliasModelClass associationClass")
    aliasGroups = [
        aGroup(person.Email, "Email", Email, PersonEmailAssociation),
        aGroup(person.Role, "Role", Role, PersonRoleAssociation),
        aGroup(person.ClassYear, "Year", ClassYear, PersonYearAssociation),
        aGroup(person.School, "School", School, PersonSchoolAssociation)
    ]
    # add aliases (records for fields that may have more than one entry (Email, School affiliation, etc))
    editedBools = []
    for group in aliasGroups:
        editedBools.append(
            insertAliasIfNotExists(dbSession, ID, group.aliasValue, group.aliasColumnName, group.aliasModelClass,
                                   group.associationClass))
    edited = np.any(editedBools) or edited

    # add the contact list if necessary. add the association too
    listID = findExistingListID(dbSession, person.ContactList)
    if listID is None:
        newContactListEntry = ContactList(
            ListName=person.ContactList,
            CsvFilePath=person.CsvFilePath,
            Date=timestamp()
        )
        dbSession.add(newContactListEntry)
        edited = True
        dbSession.commit()
        listID = newContactListEntry.TableID
    statement = insert(PersonContactListAssociation).values(
        PersonID=person.ID,
        ContactListID=listID
    )
    try:
        dbSession.execute(statement)
    except Exception as e:
        # pass
        print("Couldn't add list association (probably just a repeat):", repr(e))

    if not new:
        if edited:
            logger.info(f"Updated person with ID {ID}")
            pEntry = dbSession.query(Person).filter_by(ID=ID).first()
            if pEntry:
                pEntry.DateLastEdited = timestamp()
        else:
            print("No updates needed for contact with ID", ID)

    dbSession.commit()
    dbSession.close()  # closing the db, not the connection
    return True, ID, not match


if __name__ == "__main__":
    p = schemas.PersonSchema(firstName="Joe", lastName="Smith", phoneNumber="1111111111",
                             contactList="TestAPIList1", classYear=2026, email="joe@smith.com", role="Test",
                             school="CMC")
    print(addRecord(p))
