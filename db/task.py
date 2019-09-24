from sqlalchemy import Column, String, TIMESTAMP

from db.basic import Base


class Task(Base):
    __tablename__ = 'tasks'

    cid = Column(String, primary_key=True)
    time = Column(TIMESTAMP)

    def __init__(self, cid, time):
        self.cid = cid
        self.time = time
