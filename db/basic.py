import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

_engine = create_engine("postgresql://%s:%s@/%s?host=%s" %
                        (os.environ["DB_USER"],
                         os.environ["DB_PASSWORD"],
                         os.environ["DB_DATABASE"],
                         os.environ["DB_HOST"]), echo=True)

_SessionFactory = sessionmaker(bind=_engine)

Base = declarative_base()


def session_factory():
    Base.metadata.create_all(_engine)
    return _SessionFactory()
