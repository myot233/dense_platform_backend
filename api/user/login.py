import datetime
from typing import Any

from fastapi import APIRouter

from database.api import *
from response import Response
from pydantic import BaseModel
import jwt

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(Response):
    def __init__(self, /, **data: Any):
        super().__init__(**data)

    token: str | None


def makeAccountJwt(account: str) -> str:
    secret = "this_is_the_secret"
    payload = {
        "account": account,
        "exp": datetime.datetime.now() + datetime.timedelta(days=30),
    }
    return jwt.encode(payload, secret, algorithm='HS256')


@router.post("/api/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    Session = sessionmaker(bind=engine)
    session = Session()
    with session:
        user = queryAccount(session, request.username, request.password)
        if user is None:
            return LoginResponse(code=31, message="错误的账号或者密码", token=None)
        return LoginResponse(token=makeAccountJwt(user.id))


@router.post("/api/register", response_model=LoginResponse)
async def register(request: LoginRequest):
    Session = sessionmaker(bind=engine)
    session = Session()
    with session:
        user = addUserAccount(session, request.username, request.password)
        if not user:
            return LoginResponse(code=32, message="已存在的账号", token=None)
        return LoginResponse(token=makeAccountJwt(request.username))

