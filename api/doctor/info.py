import typing

from fastapi import APIRouter
from sqlalchemy.orm import sessionmaker

from database.db import engine
from database.table import UserType, Doctor as tDoctor, User, UserSex
from utils.response import Response
from utils import resolveAccountJwt
from utils.request import TokenRequest
from pydantic import BaseModel

router = APIRouter()


class Doctor(BaseModel):
    id: str
    name: str
    sex: UserSex
    position: str = ""
    workplace: str = ""


class DoctorResponse(Response):
    doctors: typing.List[Doctor]


@router.post("/api/doctors")
async def doctors(request: TokenRequest):
    username = resolveAccountJwt(request.token)["account"]
    session = sessionmaker(bind=engine)()
    _doctors = []
    with session:
        query_doctors = session.query(User).filter(User.type == UserType.Doctor).all()
        for doctor in query_doctors:
            tD = session.query(tDoctor).filter(tDoctor.id == doctor.id).first()
            detail = doctor.user_detail
            (name, sex) = (doctor.id, UserSex.Male) if detail is None else (detail.name, detail.sex)
            (position, workplace) = ("", "") if tD is None else (tD.workplace, tD.position)
            _doctors.append(Doctor(id=doctor.id, name=name, sex=sex, position=position, workplace=workplace))
        return DoctorResponse(doctors=_doctors)
