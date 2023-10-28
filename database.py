
import datetime

from sqlalchemy import Column, DateTime, Integer, String, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from conversation import Base

engine = create_engine('sqlite:///conversations.db')
Base.metadata.create_all(engine)


Session = scoped_session(sessionmaker(bind=engine))

