import sqlite3


def createDatabase(dbPath):
    con = sqlite3.connect(dbPath)
    cur = con.cursor()

    # create Person table (master)
    cur.execute(
        """
        CREATE TABLE "Person" (
            "ID"	INTEGER NOT NULL UNIQUE,
            "FirstName"	TEXT NOT NULL,
            "LastName"	TEXT,
            "PhoneNumber"	TEXT UNIQUE,
            "DateAdded"	TEXT NOT NULL,
            "DateLastEdited"	TEXT NOT NULL,
            PRIMARY KEY("ID" AUTOINCREMENT)
        )
        """
    )

    # create class year table
    cur.execute("""
    CREATE TABLE "ClassYear" (
        "TableID"	INTEGER NOT NULL UNIQUE,
        "Year"	INTEGER NOT NULL UNIQUE,
        PRIMARY KEY("TableID" AUTOINCREMENT)
    )
    """)

    # create table to keep track of what lists our contacts appear on
    cur.execute("""
        CREATE TABLE "ContactList" (
        "TableID"	INTEGER NOT NULL UNIQUE,
        "ListName"	TEXT NOT NULL UNIQUE,
        "CsvFilePath" TEXT,
        "Date"	TEXT NOT NULL,
        PRIMARY KEY("TableID" AUTOINCREMENT)
    )""")

    # create tables storing emails
    cur.execute(
        """
        CREATE TABLE "Email" (
            "TableID"	INTEGER NOT NULL UNIQUE,
            "Email"	TEXT NOT NULL UNIQUE,
            PRIMARY KEY("TableID" AUTOINCREMENT)
        )""")

    # create table to store the roles a contact has
    cur.execute("""
        CREATE TABLE "Role" (
        "TableID"	INTEGER NOT NULL UNIQUE,
        "Role"	TEXT NOT NULL UNIQUE,
        PRIMARY KEY("TableID" AUTOINCREMENT)
        )""")

    # create table to store which schools a contact is affiliated with
    cur.execute("""
    CREATE TABLE "School" (
        "TableID"	INTEGER NOT NULL UNIQUE,
        "School"	TEXT NOT NULL UNIQUE,
        PRIMARY KEY("TableID" AUTOINCREMENT)
    )""")

# associations

    cur.execute("""
    CREATE TABLE "PersonContactListAssociation" (
        "PersonID" INTEGER,
        "ContactListID" INTEGER,
        PRIMARY KEY (PersonID, ContactListID),
        FOREIGN KEY(PersonID) REFERENCES "Person"(ID),
        FOREIGN KEY(ContactListID) REFERENCES "ContactList"(TableID)
    )""")

    cur.execute("""
    CREATE TABLE "PersonYearAssociation" (
        "PersonID" INTEGER,
        "AssocID" INTEGER,
        PRIMARY KEY (PersonID, AssocID),
        FOREIGN KEY(PersonID) REFERENCES "Person"(ID),
        FOREIGN KEY(AssocID) REFERENCES "ClassYear"(TableID)
    )""")

    cur.execute("""
    CREATE TABLE "PersonEmailAssociation" (
        "PersonID" INTEGER,
        "AssocID" INTEGER,
        PRIMARY KEY (PersonID, AssocID),
        FOREIGN KEY(PersonID) REFERENCES "Person"(ID),
        FOREIGN KEY(AssocID) REFERENCES "Email"(TableID)
    )""")

    cur.execute("""
    CREATE TABLE "PersonSchoolAssociation" (
        "PersonID" INTEGER,
        "AssocID" INTEGER,
        PRIMARY KEY (PersonID, AssocID),
        FOREIGN KEY(PersonID) REFERENCES "Person"(ID),
        FOREIGN KEY(AssocID) REFERENCES "School"(TableID)
    )""")

    cur.execute("""
    CREATE TABLE "PersonRoleAssociation" (
        "PersonID" INTEGER,
        "AssocID" INTEGER,
        PRIMARY KEY (PersonID, AssocID),
        FOREIGN KEY(PersonID) REFERENCES "Person"(ID),
        FOREIGN KEY(AssocID) REFERENCES "Role"(TableID)
    )""")

if __name__ == "__main__":
    createDatabase("contacts.db")
