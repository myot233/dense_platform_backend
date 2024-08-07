# coding: utf-8
import enum

from sqlalchemy import CHAR, Column, Date, DateTime, Enum, ForeignKey, LargeBinary, String, text
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class UserType(enum.Enum):
    Patient = 0
    Doctor = 1


class ImageType(enum.Enum):
    source = 0
    result = 1


class Image(Base):
    __tablename__ = 'image'

    id = Column(BIGINT(20), primary_key=True)
    data = Column(LargeBinary, nullable=False)
    upload_time = Column(DateTime, nullable=False, server_default=text("current_timestamp()"))
    format = Column(String(25), server_default=text("jpg"))


class DenseImage(Image):
    __tablename__ = 'dense_image'

    id = Column(ForeignKey('image.id'), primary_key=True)
    report = Column(ForeignKey('dense_report.id'), nullable=False, index=True)
    image = Column(BIGINT(20), nullable=False, index=True)
    _type = Column(Enum(ImageType), nullable=False)

    dense_report = relationship('DenseReport')


class User(Base):
    __tablename__ = 'user'

    id = Column(String(20), primary_key=True)
    password = Column(CHAR(64), nullable=False)
    _type = Column(Enum(UserType), nullable=False)


class Doctor(User):
    __tablename__ = 'doctor'

    id = Column(ForeignKey('user.id'), primary_key=True)
    position = Column(String(20))
    workplace = Column(String(20))


class UserDetail(User):
    __tablename__ = 'user_detail'

    id = Column(ForeignKey('user.id'), primary_key=True)
    name = Column(String(20))
    sex = Column(Enum('Female', 'Male'))
    birth = Column(Date)
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(String(100))
    avatar = Column(ForeignKey('image.id'), index=True)

    image = relationship('Image')


class DenseReport(Base):
    __tablename__ = 'dense_report'

    id = Column(BIGINT(20), primary_key=True)
    user = Column(ForeignKey('user.id'), unique=True)
    doctor = Column(ForeignKey('user.id'), index=True)
    submitTime = Column(Date,server_default=text("current_timestamp()"))
    current_status = Column(Enum('Checking', 'Completed', 'Abnormality', 'Error'), server_default=text("'Checking'"))

    user1 = relationship('User', primaryjoin='DenseReport.doctor == User.id')
    user2 = relationship('User', primaryjoin='DenseReport.user == User.id')


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(BIGINT(20), primary_key=True)
    report = Column(ForeignKey('dense_report.id'), nullable=False, index=True)
    content = Column(String(4096))

    dense_report = relationship('DenseReport')
