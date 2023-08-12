from collections import namedtuple
from datetime import datetime
import pandas as pd, numpy as np
import schemas
import dbConfig
from models import Person, Email, Role, ClassYear, School, ContactList
from sqlalchemy.orm import aliased
from line_profiler_pycharm import profile


import cProfile
import io
import pstats
import contextlib


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
        dbSession.query(ContactList).filter((ContactList.ListName == listName) & (ContactList.ID == ID))
    )
    res = query.first()
    return res is not None


@profile
def findExistingContactID(db, person):
    p = aliased(Person)
    ea = aliased(Email)
    # a row matches if it meets the following:
    # row.Email == person.Email OR (row.PhoneNumber = person.PhoneNumber AND person.PhoneNumber is not None)
    # AND
    # row.PhoneNumber is None  OR (row.PhoneNumber = person.PhoneNumber AND person.PhoneNumber is not None) OR person.PhoneNumber is None

    if person.Email:
        query = (
            db.query(p.ID)
            .join(ea, p.ID == ea.ID)
            .filter(
                ((ea.Email == person.Email) | (
                        (p.PhoneNumber == person.PhoneNumber) & (person.PhoneNumber is not None))) &
                ((p.PhoneNumber.is_(None)) | ((p.PhoneNumber == person.PhoneNumber) & p.PhoneNumber.is_not(None)) |
                 (person.PhoneNumber is None))
            )
        )
    else:
        query = (
            db.query(p.ID)
            .filter(p.PhoneNumber == person.PhoneNumber)
        )

    res = query.all()
    ID = None
    if res:
        ID = res[0][0]
        if len(res) > 1:
            print("Uh oh. multiple results")
    return bool(res), ID


@profile
def getPersonRecord(dbSession, ID):
    person = dbSession.query(Person).filter(Person.ID == ID).first()
    return person


# this function uses 'alias/Alias' to mean any new value/column/class for a table that is allowed
# to store multiple fields for each person. this includes the name
# this can be a little confusing:
@profile
def insertAlias(dbSession, personId, aliasValue, aliasModelClass, aliasColumnName):
    # print("Update!", "ID:", personId, "alias:", aliasTableName, "value:", aliasValue)
    newAlias = aliasModelClass(ID=personId)
    setattr(newAlias, aliasColumnName, aliasValue)
    dbSession.add(newAlias)
    dbSession.commit()


@profile
def insertAliasIfNotExists(dbSession, personId, aliasValue, aliasColumnName, aliasModelClass):
    # check if the alias already exists for the person
    if aliasValue is not None and not pd.isna(aliasValue):
        existingAlias = (
            dbSession.query(getattr(aliasModelClass, aliasColumnName))
            .filter(getattr(aliasModelClass, 'ID') == personId, getattr(aliasModelClass, aliasColumnName) == aliasValue)
            .first()
        )

        if not existingAlias:
            # insert the new alias for the person
            # with profiled():
            insertAlias(dbSession, personId, aliasValue, aliasModelClass, aliasColumnName)
        return
    # print("DID not edit alias", aliasColumnName, "for person #" + str(personId),
    #       "because the provIDed value was None.")


@profile
def addRecord(person: schemas.PersonSchema):
    dbSession = dbConfig.dbSession

    edited = False
    if pd.isna(person.Email) and pd.isna(person.PhoneNumber):
        print(
            f"{tcolors.BOLD}{tcolors.FAIL}WARNING: Contact {person.FirstName} {person.LastName} skipped. Must have Email or phone number.{tcolors.ENDC}")
        return False, -1, False

    match, ID = findExistingContactID(dbSession, person)  # are there one or more matches already in the db?

    if match:
        # ---- record exists, we need to update it ----
        # if len(match) > 1:
        #     raise ValueError("Something is wrong. ID {} gets more than one result!".format(ID))  # uh oh
        personRecord = getPersonRecord(dbSession, ID)
        if not personRecord:
            raise ValueError("Internal error: no person with ID {} exists!".format(ID))
        # print("Existing contact:", FirstName, LastName, "ID:", ID)

        if person.PhoneNumber != personRecord.PhoneNumber:  # yippee, we got a phone #
            dbSession.query(Person).filter_by(ID=ID).update({"PhoneNumber": person.PhoneNumber})

        if person.FirstName and person.FirstName != personRecord.FirstName:
            personRecord.FirstName = person.FirstName
            edited = True
        if person.LastName and person.LastName != personRecord.LastName:
            personRecord.LastName = person.FirstName
            edited = True

    else:  # this is a new person
        if not person.FirstName and not person.LastName:
            raise ValueError("Error with ID {}: Both names cannot be blank when inserting contact.".format(ID))
        latestId = dbSession.query(Person.ID).order_by(Person.ID.desc()).limit(1).scalar()
        ID = int(
            latestId) + 1 if latestId is not None else 0  # our indexing is just to increment each ID by one. real advanced stuff
        #  ----- no record exists, we need to make a new one -----
        print("New contact:", person.FirstName, person.LastName, "ID:", ID)
        # add record, Email, School, alias, Role, etc
        person.ID = ID
        person.DateAdded, person.DateLastEdited = timestamp(), timestamp()
        newPerson = schemas.personSchemaToModel(person)

        dbSession.add(newPerson)

    aGroup = namedtuple("AliasGroup", "aliasValue aliasColumnName aliasModelClass")
    aliasGroups = [
        aGroup(person.Email, "Email", Email),
        aGroup(person.Role, "Role", Role),
        aGroup(person.ClassYear, "Year", ClassYear),
        aGroup(person.School, "School", School)
    ]
    # add aliases (records for fields that may have more than one entry (Email, School affiliation, etc))
    editedBools = []
    for group in aliasGroups:
        editedBools.append(
            insertAliasIfNotExists(dbSession, ID, group.aliasValue, group.aliasColumnName, group.aliasModelClass))
    edited = np.any(editedBools) or edited

    if not IDIsOnList(dbSession, person.ContactList, ID):
        newContactListEntry = ContactList(
            ID=ID,
            ListName=person.ContactList,
            Date=timestamp()
        )
        dbSession.add(newContactListEntry)
        edited = True
    if edited:
        print("Updated person with ID", ID)
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
