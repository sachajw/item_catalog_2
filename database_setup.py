from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__= 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Book(Base):
    __tablename__ = 'book'

    id = Column(Integer, primary_key=True)
    title = Column(String(500), unique=True, nullable=False, index=True)
    author = Column(String(350))
    genre = Column(String(50))
    format = Column(String(50))
    image = Column(String(250))
    num_pages = Column(Integer)
    pub_date = Column(String(20))
    pub_name = Column(String(80))
    pub_id = Column(String(10))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

engine = create_engine('sqlite:///bookcatalogue.db')

Base.metadata.create_all(engine)
