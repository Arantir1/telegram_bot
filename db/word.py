from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime

from db.basic import Base


class Word(Base):
    __tablename__ = 'words'

    now = datetime.now()

    id = Column(Integer, autoincrement=True, primary_key=True)
    word = Column(String,)
    cid = Column(String,)
    last_repeat = Column(DateTime(), default=now)
    iteration = Column(Integer, default=1)
    next_repeat = Column(DateTime(), default=(now + timedelta(days=1)))

    def __init__(self, word, cid):
        self.word = word
        self.cid = cid
