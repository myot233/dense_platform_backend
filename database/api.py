import sqlalchemy.exc
from pymysql import IntegrityError
from sqlalchemy.orm import sessionmaker
from .table import UserAccount, UserDetail
from sqlalchemy import and_, or_, func

from .db import engine


def queryInfo(session, username: str) -> UserDetail:
    user = session.query(UserDetail).filter(UserDetail.id == username).first()
    session.commit()
    return user


def deleteInfo(session, username: str) -> UserDetail:
    user = session.query(UserDetail).filter(UserDetail.id == username).first()
    if user is not None:
        session.delete(user)
        session.commit()


def addInfo(session, userinfo: UserDetail):
    try:
        session.add(userinfo)
        session.commit()
    except sqlalchemy.exc.IntegrityError as err:
        session.rollback()
        return False
    return True


def queryAccount(session, account: str, password: str) -> UserAccount:
    user = session.query(UserAccount).filter(
        and_(UserAccount.id == account, UserAccount.password == password)).first()
    session.commit()
    return user


def addUserAccount(session, account: str, password: str) -> bool:
    user = UserAccount(id=account, password=password)
    try:
        session.add(user)
        session.commit()
    except sqlalchemy.exc.IntegrityError as err:

        session.rollback()
        return False
    return True


if __name__ == '__main__':
    Session = sessionmaker(bind=engine)
    session = Session()
