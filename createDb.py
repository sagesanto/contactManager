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
            "PhoneNumber"	INTEGER,
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
            "ID"	INTEGER NOT NULL,
            "First"	TEXT,
            "Last"	TEXT,
            FOREIGN KEY(ID) REFERENCES Person(ID)
        )
        """
    )

    # Create class year table
    cur.execute("""
    CREATE TABLE "ClassYear" (
        "ID"	INTEGER NOT NULL,
        "Year"	INTEGER NOT NULL,
        FOREIGN KEY(ID) REFERENCES Person(ID)
    )
    """)

    # create table to keep track of what lists our contacts appear on
    cur.execute("""
        CREATE TABLE "ContactList" (
        "ID"	INTEGER NOT NULL,
        "ListName"	TEXT NOT NULL,
        "Date"	TEXT NOT NULL,
        FOREIGN KEY(ID) REFERENCES Person(ID)
    )""")

    # create tables storing emails
    cur.execute(
        """
        CREATE TABLE "Email" (
            "ID"	INTEGER NOT NULL,
            "Email"	TEXT NOT NULL,
            FOREIGN KEY(ID) REFERENCES Person(ID)
        )""")

    # create table to store the roles a contact has
    cur.execute("""
        CREATE TABLE "Role" (
        "ID"	INTEGER NOT NULL,
        "Role"	TEXT NOT NULL,
        FOREIGN KEY(ID) REFERENCES Person(ID)
    )""")

    # create table to store which schools a contact is affiliated with
    cur.execute("""
    CREATE TABLE "School" (
        "ID"	INTEGER NOT NULL,
        "School"	TEXT NOT NULL,
        FOREIGN KEY(ID) REFERENCES Person(ID)
    )""")


createDatabase("contacts.db")
