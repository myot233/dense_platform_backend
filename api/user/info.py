import os
import pathlib
from typing import Any

from fastapi import APIRouter, UploadFile, Request
from pydantic import BaseModel

from database.api import *
from response import Response
from utils import (resolveAccountJwt)
from fastapi.responses import StreamingResponse

router = APIRouter()


class InfoRequest(BaseModel):
    token: str


class Form(BaseModel):
    def __init__(self, /, **data: Any):
        super().__init__(**data)

    name: str = None
    sex: str = None
    birth: str = None
    phone: str = None
    email: str = None
    address: str = None


class InfoResponse(Response):
    def __init__(self, /, **data: Any):
        super().__init__(**data)

    form: Form


@router.post("/api/info")
async def info(request: InfoRequest):
    Session = sessionmaker(bind=engine)
    session = Session()
    username = resolveAccountJwt(request.token)["account"]
    with session:
        userInfo = queryInfo(session, username)
        print(userInfo)
        if userInfo is None:
            return InfoResponse(code="33", message="用户没有设置信息", form=Form(name=username))
        return InfoResponse(
            form=Form(name=userInfo.name, sex=str("male" if userInfo.sex else "female"), birth=str(userInfo.birth),
                      phone=userInfo.phone,
                      email=userInfo.email, address=userInfo.address))


class SubmitInfoRequest(BaseModel):
    token: str
    form: Form


@router.post("/api/submitInfo")
async def submitInfo(request: SubmitInfoRequest):
    Session = sessionmaker(bind=engine)
    session = Session()
    username = resolveAccountJwt(request.token)["account"]
    with session:
        deleteInfo(session, username)
        form = request.form.dict()
        form["sex"] = False if form["sex"] == "female" else True
        form["birth"] = form["birth"].split("T")[0]
        detail = UserDetail(id=username, **form)
        addInfo(session, detail)
        return Response()


@router.post("/api/uploadAvatar")
async def uploadAvatar(request: Request):
    token = request.headers.get("token", None)
    if token is None:
        return Response(code=34, message="用户未登录")
    username = resolveAccountJwt(token)["account"]
    form = await request.form()
    file = form.get("file")
    format = file.filename.split(".")[-1]
    if os.path.exists(f"./avatar/{username}"):
        os.removedirs(f"./avatar/{username}")
    os.mkdir(f"./avatar/{username}")
    with open(f"./avatar/{username}/{username}.{format}", "wb") as f:
        f.write(file.file.read())
    return Response(code=0, message="")


class AvatarRequest(BaseModel):
    token: str


@router.post("/api/avatar")
async def avatar(request: AvatarRequest):
    username = resolveAccountJwt(request.token)["account"]
    if not os.path.exists(f"./avatar/{username}"):
        return StreamingResponse(open(f"./avatar/img.png", "rb"), media_type="image/png")
    for i in os.listdir(f"./avatar/{username}"):
        return StreamingResponse(open(f"./avatar/{username}/" + i, "rb"), media_type="image/png")
