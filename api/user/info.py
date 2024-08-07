import os
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field

from database.api import *
from response import Response
from utils import (resolveAccountJwt)

router = APIRouter()


class InfoRequest(BaseModel):
    token: str


class Form(BaseModel):
    def __init__(self, /, **data: Any):
        super().__init__(**data)

    model_config = ConfigDict(from_attributes=True)
    name: str = None
    sex: str = Field()
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
        return InfoResponse(form=Form.model_validate(userInfo))


class SubmitInfoRequest(BaseModel):
    token: str
    form: Form


@router.post("/api/submitInfo")
async def submitInfo(request: SubmitInfoRequest):
    session = sessionmaker(bind=engine)()
    username = resolveAccountJwt(request.token)["account"]
    with session:
        deleteInfo(session, username)
        form = request.form.dict()
        form["sex"] = False if form["sex"] == "female" else True
        form["birth"] = form["birth"].split("T")[0]
        detail = UserDetail(id=username, **form)
        addInfo(session, detail)
        return Response()


# @router.post("/api/uploadAvatar")
# async def uploadAvatar(request: Request):
#     token = request.headers.get("token", None)
#     if token is None:
#         return Response(code=34, message="用户未登录")
#     username = resolveAccountJwt(token)["account"]
#     form = await request.form()
#     file = form.get("file")
#     format = file.filename.split(".")[-1]
#     if os.path.exists(f"./avatar/{username}"):
#         os.removedirs(f"./avatar/{username}")
#     os.mkdir(f"./avatar/{username}")
#     with open(f"./avatar/{username}/{username}.{format}", "wb") as f:
#         f.write(file.file.read())
#     return Response(code=0, message="")


class AvatarRequest(BaseModel):
    token: str


@router.post("/api/avatar")
async def avatar(request: AvatarRequest):
    username = resolveAccountJwt(request.token)["account"]
    session = sessionmaker(bind=engine)()
    with session:
        detail = session.query(UserDetail).filter(UserDetail.id == username).first()
        data = session.query(Image).filter(detail.image == Image.id).first()
    return StreamingResponse([data.data])
