import datetime

from sqlalchemy import Column, DateTime, Integer, String, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True)
    input_text = Column(String, nullable=False)
    output_text = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

