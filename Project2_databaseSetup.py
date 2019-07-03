import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()
print('creatingbase')


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)


@property
def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'email': self.email,
            'name': self.name,
            'id': self.id,
        }


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


@property
def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(500), nullable=False)
    cat_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship(Category)


@property
def serialize(self):
    return {
        'name': self.name,
        'description': self.description,
        'id': self.id,
        }


engine = create_engine('sqlite:///catalogapp.db')
Base.metadata.create_all(engine)
