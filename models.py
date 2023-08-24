# SQLAlchemy models for each table
from typing import List

from sqlalchemy import Column, Integer, String, ForeignKey, Table, PrimaryKeyConstraint
from sqlalchemy.orm import relationship, backref, Mapped, mapped_column
from dbConfig import Base
from sqlalchemy_to_pydantic import sqlalchemy_to_pydantic

PersonContactListAssociation = Table(
    'PersonContactListAssociation',
    Base.metadata,
    Column('PersonID', Integer, ForeignKey('Person.ID'), nullable=False),
    Column('ContactListID', Integer, ForeignKey('ContactList.TableID'), nullable=False),
    PrimaryKeyConstraint('PersonID', 'ContactListID')
)

PersonYearAssociation = Table(
    'PersonYearAssociation',
    Base.metadata,
    Column('PersonID', Integer, ForeignKey('Person.ID'), nullable=False),
    Column('AssocID', Integer, ForeignKey('ClassYear.TableID'), nullable=False),
    PrimaryKeyConstraint('PersonID', 'AssocID')
)

PersonEmailAssociation = Table(
    'PersonEmailAssociation',
    Base.metadata,
    Column('PersonID', Integer, ForeignKey('Person.ID'), nullable=False),
    Column('AssocID', Integer, ForeignKey('Email.TableID'), nullable=False),
    PrimaryKeyConstraint('PersonID', 'AssocID')
)

PersonRoleAssociation = Table(
    'PersonRoleAssociation',
    Base.metadata,
    Column('PersonID', Integer, ForeignKey('Person.ID'), nullable=False),
    Column('AssocID', Integer, ForeignKey('Role.TableID'), nullable=False),
    PrimaryKeyConstraint('PersonID', 'AssocID')
)

PersonSchoolAssociation = Table(
    'PersonSchoolAssociation',
    Base.metadata,
    Column('PersonID', Integer, ForeignKey('Person.ID'), nullable=False),
    Column('AssocID', Integer, ForeignKey('School.TableID'), nullable=False),
    PrimaryKeyConstraint('PersonID', 'AssocID')
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
    ContactLists: Mapped[List["ContactList"]] = relationship("ContactList", secondary=PersonContactListAssociation, back_populates="People", cascade="all, delete")
    ClassYears: Mapped[List["ClassYear"]] = relationship("ClassYear", secondary=PersonYearAssociation, back_populates="People", cascade="all, delete")
    Emails: Mapped[List["Email"]] = relationship("Email", secondary=PersonEmailAssociation, back_populates="People", cascade="all, delete")
    Roles: Mapped[List["Role"]] = relationship("Role", secondary=PersonRoleAssociation, back_populates="People", cascade="all, delete")
    Schools: Mapped[List["School"]] = relationship("School", secondary=PersonSchoolAssociation, back_populates="People", cascade="all, delete")


# not currently in use
# class NameAlias(Base):
#     __tablename__ = 'NameAlias'
#
#     ID = Column(Integer, ForeignKey('Person.ID'), primary_key=True)
#     First = Column(String)
#     Last = Column(String)
#
#     Person = relationship('Person', back_populates='Aliases')

class ContactList(Base):
    __tablename__ = 'ContactList'

    TableID: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True, autoincrement=True)
    ListName = Column(String, nullable=False, unique=True, index=True)
    CsvFilePath = Column(String)
    Date = Column(String, nullable=False)
    People: Mapped[List["Person"]] = relationship("Person", secondary=PersonContactListAssociation,
                                                  back_populates="ContactLists")

    def __str__(self):
        return self.ListName


class ClassYear(Base):
    __tablename__ = 'ClassYear'

    TableID: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True, autoincrement=True)
    Year = Column(Integer, nullable=False, unique=True, index=True)
    People: Mapped[List["Person"]] = relationship("Person", secondary=PersonYearAssociation, back_populates="ClassYears")

    def __str__(self):
        return str(self.Year)


class Email(Base):
    __tablename__ = 'Email'

    TableID: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True, autoincrement=True)
    Email = Column(String, nullable=False)
    People: Mapped[List["Person"]] = relationship("Person", secondary=PersonEmailAssociation,
                                                  back_populates="Emails")
    def __str__(self):
        return self.Email


class Role(Base):
    __tablename__ = 'Role'

    TableID: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True, autoincrement=True)
    Role = Column(String, nullable=False, unique=True, index=True)
    People: Mapped[List["Person"]] = relationship("Person", secondary=PersonRoleAssociation, back_populates="Roles")

    def __str__(self):
        return self.Role


# class Role(Base):
#     __tablename__ = 'Role'
#
#     TableID: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True, autoincrement=True)
#     PersonID: Mapped[int] = mapped_column(Integer, ForeignKey('Person.ID'))
#     Role = Column(String, nullable=False)
#     Person: Mapped["Person"] = relationship(back_populates="Roles")
#
#     def __str__(self):
#         return self.Role

class School(Base):
    __tablename__ = 'School'

    TableID: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True, autoincrement=True)
    School = Column(String, nullable=False, unique=True, index=True)
    People: Mapped[List["Person"]] = relationship("Person", secondary=PersonSchoolAssociation, back_populates="Schools")

    def __str__(self):
        return self.School
