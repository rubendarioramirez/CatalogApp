import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))
 
class Category(Base):
    __tablename__ = 'category'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship(User)
 
class CategoryItem(Base):
    __tablename__ = 'category_item'

    name =Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    description = Column(String(250))
    price = Column(String(8))
    category_id = Column(Integer,ForeignKey('category.id'))
    category = relationship(Category) 
    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship(User)

    #We added this serialize function to be able to send JSON objects in a serializable format
    @property
    def serialize(self):       
        return {
        'name': self.name,
        'description':  self.description,
        'id':   self.id,
        'price':    self.price,
        }

engine = create_engine('sqlite:///catalogUser.db')

Base.metadata.create_all(engine)

#### https://www.udacity.com/course/viewer#!/c-ud088-nd/l-3621198668/m-3630068948 
#### Crud review con todos los casos: ADD, DELETE, UPDATE, RETRIEVE