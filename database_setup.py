import os
import sys
from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Publication(Base):
    #Mapper
    __tablename__ = 'publication'
    #Table
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)

    @property
    def serialize(self):
        """Return object data in serializeable format"""
        return {
            'id' : self.id,
            'name' : self.name,
        }

class Book(Base):
    #Mapper
    __tablename__ = 'book'
    #Table
    id = Column(Integer, primary_key=True)
    title = Column(String(500), unique=True, nullable=False, index=True)
    author = Column(String(350))
    genre = Column(String(50))
    format = Column(String(50))
    image = Column(String(250))
    num_pages = Column(Integer)
    pub_date = Column(String(20))
    pub_name = Column(String(80))
    user_id = Column(Integer, ForeignKey('users.id'))

    @property
    def serialize(self):
        """Return object data in serializeable format"""
        return {
            'id' : self.id,
            'title' : self.title,
            'author' : self.author,
            'avg_rating' : self.avg_rating,
            'format' : self.format,
            'image' : self.image,
            'num_pages' : self.num_pages,
            'pub_date' : self.pub_date,
        }

class User(Base):
    #Mapper
    __tablename__= 'users'
    #Table
    id = Column(Integer, primary_key=True)
    user_name = Column(String(30))
    user_email = Column(String(60), unique=True, index=True)
    user_password = Column(String(80))
    registration_date = Column(String(20), nullable=False, default=datetime.now())
    user_id = Column(Integer, ForeignKey('users.id'))


engine = create_engine('sqlite:///bookcatalogue.db')

Base.metadata.create_all(engine)
