
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import datetime
engine = create_engine('sqlite:///conversations.db')

Session = scoped_session(sessionmaker(bind=engine))

