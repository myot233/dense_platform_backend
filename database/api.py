from datetime import datetime
from typing import List

import sqlalchemy.exc
from pymysql import IntegrityError
from sqlalchemy.orm import sessionmaker, Session

from .table import UserDetail, DenseReport, User, UserType, Image
from sqlalchemy import and_, or_, func

from .db import engine


def addReport(_session, user: str, doctor: str, fileId: str) -> DenseReport:
    report = DenseReport(user=user, doctor=doctor, image=fileId, submitTime=datetime.now().date(),
                         current_status='检测中')
    _session.add(report)
    _session.commit()
    return report


def get_reports(_session: Session, id: str) -> List[DenseReport]:
    reports = _session.query(DenseReport).filter(DenseReport.user == id).all()
    _session.commit()
    return reports


def queryInfo(_session, username: str) -> UserDetail:
    user = _session.query(UserDetail).filter(UserDetail.id == username).first()
    _session.commit()
    return user


def deleteInfo(_session, username: str):
    user = _session.query(UserDetail).filter(UserDetail.id == username).first()
    if user is not None:
        _session.delete(user)
        _session.commit()


def uploadImage(_session: Session, file_name: str, data: bytes) -> int:
    image = Image(format=file_name.split(".")[-1], data=data)
    _session.add(image)
    _session.commit()
    return image.id


def addInfo(_session, userinfo: UserDetail):
    try:
        _session.add(userinfo)
        _session.commit()
    except sqlalchemy.exc.IntegrityError as err:
        _session.rollback()
        return False
    return True


def queryAccount(_session, account: str, password: str) -> User:
    user = _session.query(User).filter(
        and_(User.id == account, User.password == password)).first()
    _session.commit()
    return user


def addUserAccount(_session: Session, account: str, password: str, _type: UserType) -> bool:
    user = User(id=account, password=password, _type=_type)
    try:
        _session.add(user)
        _session.commit()
    except sqlalchemy.exc.IntegrityError as err:

        _session.rollback()
        return False
    return True


if __name__ == '__main__':
    Session = sessionmaker(bind=engine)
    session = Session()
