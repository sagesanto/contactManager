# SQLAlchemy models for each table

from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from dbConfig import Base


class Person(Base):
    __tablename__ = 'Person'

    ID = Column(Integer, primary_key=True, autoincrement=True)
    FirstName = Column(String, nullable=False)
    LastName = Column(String)
    PhoneNumber = Column(String)
    DateAdded = Column(String, nullable=False)
    DateLastEdited = Column(String, nullable=False)

    # Aliases = relationship('Alias', back_populates='Person')
    ClassYears = relationship('ClassYear', back_populates='Person')
    ContactLists = relationship('ContactList', back_populates='Person')
    Emails = relationship('Email', back_populates='Person')
    Roles = relationship('Role', back_populates='Person')
    Schools = relationship('School', back_populates='Person')

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

    ID = Column(Integer, ForeignKey('Person.ID'), primary_key=True)
    Year = Column(Integer, nullable=False)

    Person = relationship('Person', back_populates='ClassYears')


class ContactList(Base):
    __tablename__ = 'ContactList'

    ID = Column(Integer, ForeignKey('Person.ID'), primary_key=True)
    ListName = Column(String, nullable=False)
    Date = Column(String, nullable=False)

    Person = relationship('Person', back_populates='ContactLists')


class Email(Base):
    __tablename__ = 'Email'

    ID = Column(Integer, ForeignKey('Person.ID'), primary_key=True)
    Email = Column(String, nullable=False)

    Person = relationship('Person', back_populates='Emails')


class Role(Base):
    __tablename__ = 'Role'

    ID = Column(Integer, ForeignKey('Person.ID'), primary_key=True)
    Role = Column(String, nullable=False)

    Person = relationship('Person', back_populates='Roles')


class School(Base):
    __tablename__ = 'School'

    ID = Column(Integer, ForeignKey('Person.ID'), primary_key=True)
    School = Column(String, nullable=False)

    Person = relationship('Person', back_populates='Schools')
