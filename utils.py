# utils.py
import datetime

from conversation import Conversation
from database import Session


def store_data(input_text, output_text):
    with Session() as session:
        conversation = Conversation(input_text=input_text, output_text=output_text)
        session.add(conversation)
        session.commit()

def get_data_in_date_range(start_date, end_date):
    with Session() as session:
        data = session.query(Conversation).filter(Conversation.created_at.between(start_date, end_date)).all()
        return data

def get_last_n_days(n=5):
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=n)
    return get_data_in_date_range(start_date, end_date)

def get_last_n(n=5):
    with Session() as session:
        data = session.query(Conversation).order_by(Conversation.created_at.desc()).limit(n).all()
        return data