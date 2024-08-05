from sqlalchemy import Column, BIGINT, String, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base

if __name__ != '__main__':
    from .db import engine
else:
    from db import engine
Base = declarative_base()


class UserAccount(Base):
    __tablename__ = 'users'
    id = Column(String(20), primary_key=True)
    password = Column(String(20))


class UserDetail(Base):
    __tablename__ = 'user_details'
    id = Column(String(20), primary_key=True)
    name = Column(String(20))
    sex = Column(Boolean)
    birth = Column(Date)
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(String(100))


class DenseReport(Base):
    __tablename__ = 'dense_report'
    id = Column(BIGINT, primary_key=True)
    doctor = Column(String(20))
    image = Column(String(20))
    submitTime = Column(Date)
    current_status = Column(String(20))


if __name__ == '__main__':
    engine.connect()

    Base.metadata.create_all(engine)
