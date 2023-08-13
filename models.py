# SQLAlchemy models for each table
from typing import List

from sqlalchemy import Column, Integer, String, ForeignKey, Table, PrimaryKeyConstraint
from sqlalchemy.orm import relationship, backref, Mapped, mapped_column
from dbConfig import Base


PersonContactListAssociation = Table(
    'PersonContactListAssociation',
    Base.metadata,
    Column('PersonID', Integer, ForeignKey('Person.ID'), nullable=False),
    Column('ContactListID', Integer, ForeignKey('ContactList.TableID'), nullable=False),
    PrimaryKeyConstraint('PersonID', 'ContactListID')
)


class Person(Base):
    __tablename__ = 'Person'

    ID: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    FirstName = Column(String, nullable=False)
    LastName = Column(String)
    PhoneNumber = Column(String)
    DateAdded = Column(String, nullable=False)
    DateLastEdited = Column(String, nullable=False)

    # Aliases = relationship('Alias', back_populates='Person')
    ClassYears: Mapped[List["ClassYear"]] = relationship(back_populates="Person")
    ContactLists: Mapped[List["ContactList"]] = relationship(
        "ContactList",
        secondary=PersonContactListAssociation,
        back_populates="People")
    Emails: Mapped[List["Email"]] = relationship(back_populates="Person")
    Roles: Mapped[List["Role"]] = relationship(back_populates="Person")
    Schools: Mapped[List["School"]] = relationship(back_populates="Person")


# not currently in use
# class NameAlias(Base):
#     __tablename__ = 'NameAlias'
#
#     ID = Column(Integer, ForeignKey('Person.ID'), primary_key=True)
#     First = Column(String)
#     Last = Column(String)
#
#     Person = relationship('Person', back_populates='Aliases')


class ClassYear(Base):
    __tablename__ = 'ClassYear'

    TableID: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True, autoincrement=True)
    PersonID: Mapped[int] = mapped_column(Integer, ForeignKey('Person.ID'))
    Year = Column(Integer, nullable=False)
    Person: Mapped["Person"] = relationship(back_populates="ClassYears")


class ContactList(Base):
    __tablename__ = 'ContactList'

    TableID: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True, autoincrement=True)
    ListName = Column(String, nullable=False)
    CsvFilePath = Column(String)
    Date = Column(String, nullable=False)
    People: Mapped[List["Person"]] = relationship("Person", secondary=PersonContactListAssociation, back_populates="ContactLists")


class Email(Base):
    __tablename__ = 'Email'

    TableID: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True, autoincrement=True)
    PersonID: Mapped[int] = mapped_column(Integer, ForeignKey('Person.ID'))
    Email = Column(String, nullable=False)
    Person: Mapped["Person"] = relationship(back_populates="Emails")


class Role(Base):
    __tablename__ = 'Role'

    TableID: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True, autoincrement=True)
    PersonID: Mapped[int] = mapped_column(Integer, ForeignKey('Person.ID'))
    Role = Column(String, nullable=False)
    Person: Mapped["Person"] = relationship(back_populates="Roles")


class School(Base):
    __tablename__ = 'School'

    TableID: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True, autoincrement=True)
    PersonID: Mapped[int] = mapped_column(Integer, ForeignKey('Person.ID'))
    School = Column(String, nullable=False)
    Person: Mapped["Person"] = relationship(back_populates="Schools")
