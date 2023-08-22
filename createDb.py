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
            "PhoneNumber"	INTEGER UNIQUE,
            "DateAdded"	TEXT NOT NULL,
            "DateLastEdited"	TEXT NOT NULL,
            PRIMARY KEY("ID" AUTOINCREMENT)
        )
        """
    )

    # Create name alias table
    cur.execute(
        """
        CREATE TABLE "Alias" (
            "TableID"	INTEGER NOT NULL UNIQUE,
            "PersonID"	INTEGER NOT NULL,
            "First"	TEXT,
            "Last"	TEXT,
            PRIMARY KEY("TableID" AUTOINCREMENT),
            FOREIGN KEY(PersonID) REFERENCES Person(ID)
        )
        """
    )

    # Create class year table
    cur.execute("""
    CREATE TABLE "ClassYear" (
        "TableID"	INTEGER NOT NULL UNIQUE,
        "PersonID"	INTEGER NOT NULL,
        "Year"	INTEGER NOT NULL,
        PRIMARY KEY("TableID" AUTOINCREMENT),
        FOREIGN KEY(PersonID) REFERENCES Person(ID)
    )
    """)

    # create table to keep track of what lists our contacts appear on
    cur.execute("""
        CREATE TABLE "ContactList" (
        "TableID"	INTEGER NOT NULL UNIQUE,
        "ListName"	TEXT NOT NULL,
        "CsvFilePath" TEXT,
        "Date"	TEXT NOT NULL,
        PRIMARY KEY("TableID" AUTOINCREMENT)
    )""")

    # create tables storing emails
    cur.execute(
        """
        CREATE TABLE "Email" (
            "TableID"	INTEGER NOT NULL UNIQUE,
            "PersonID"	INTEGER NOT NULL,
            "Email"	TEXT NOT NULL,
            PRIMARY KEY("TableID" AUTOINCREMENT),
            FOREIGN KEY(PersonID) REFERENCES Person(ID)
        )""")

    # create table to store the roles a contact has
    cur.execute("""
        CREATE TABLE "Role" (
        "TableID"	INTEGER NOT NULL UNIQUE,
        "PersonID"	INTEGER NOT NULL,
        "Role"	TEXT NOT NULL,
        PRIMARY KEY("TableID" AUTOINCREMENT),
        FOREIGN KEY(PersonID) REFERENCES Person(ID)
    )""")

    # create table to store which schools a contact is affiliated with
    cur.execute("""
    CREATE TABLE "School" (
        "TableID"	INTEGER NOT NULL UNIQUE,
        "PersonID"	INTEGER NOT NULL,
        "School"	TEXT NOT NULL,
        PRIMARY KEY("TableID" AUTOINCREMENT),
        FOREIGN KEY(PersonID) REFERENCES Person(ID)
    )""")

    cur.execute("""
    CREATE TABLE "PersonContactListAssociation" (
        "PersonID" INTEGER,
        "ContactListID" INTEGER,
        PRIMARY KEY (PersonID, ContactListID),
        FOREIGN KEY(PersonID) REFERENCES "Person"(ID),
        FOREIGN KEY(ContactListID) REFERENCES "ContactList"(TableID)
    )""")


createDatabase("contacts.db")
