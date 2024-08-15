from typing import Any
from datetime import date
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy import inspect
from database.api import *
from database.table import UserSex, User as tUser
from utils.response import Response
from utils import (resolveAccountJwt)
from utils.request import TokenRequest

router = APIRouter()


class Form(BaseModel):
    def __init__(self, /, **data: Any):
        super().__init__(**data)

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    name: str = None
    sex: UserSex = None
    birth: date = None
    phone: str = None
    email: str = None
    address: str = None


class InfoResponse(Response):
    def __init__(self, /, **data: Any):
        super().__init__(**data)

    form: Form


class UserData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    type: str


class UserResponse(Response):
    user: UserData


@router.post("/api/user")
async def user(request: TokenRequest):
    _session = sessionmaker(bind=engine)()
    username = resolveAccountJwt(request.token)["account"]
    with _session:
        _user = _session.query(User).filter(User.id == username).first()
        return UserResponse(user=UserData.model_validate(_user))


@router.post("/api/info")
async def info(request: TokenRequest):
    session = sessionmaker(bind=engine)()
    username = resolveAccountJwt(request.token)["account"]
    with session:
        userInfo = queryInfo(session, username)
        if userInfo is None:
            return InfoResponse(code="33", message="用户没有设置信息", form=Form(name=username))
        return InfoResponse(form=Form.model_validate(userInfo))


class SubmitInfoRequest(TokenRequest):
    form: Form


@router.post("/api/submitInfo")
async def submitInfo(request: SubmitInfoRequest):
    session = sessionmaker(bind=engine)()
    username = resolveAccountJwt(request.token)["account"]
    with session:
        # deleteInfo(session, username)
        form = request.form.dict()
        detail = queryInfo(session, username)
        if detail is not None:
            user_detail_columns = {c.key for c in inspect(UserDetail).mapper.column_attrs}

            # 仅更新表单中存在且在UserDetail模型中的字段
            for key, value in request.form.model_dump().items():
                if key in user_detail_columns:
                    setattr(detail, key, value)

        else:
            detail = UserDetail(id=username, **form)
            addInfo(session, detail)
        session.commit()
        return Response()


class AvatarRequest(TokenRequest):
    id: int


@router.post("/api/submitAvatar")
async def submitAvatar(request: AvatarRequest):
    session = sessionmaker(bind=engine)()
    username = resolveAccountJwt(request.token)["account"]
    with session:
        detail = queryInfo(session, username)
        if detail is None:
            detail = UserDetail(id=username)
        image = session.query(Image).filter(Image.id == request.id).first()
        detail.image = image
        session.commit()
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


@router.post("/api/avatar")
async def avatar(request: TokenRequest):
    username = resolveAccountJwt(request.token)["account"]
    session = sessionmaker(bind=engine)()
    with session:
        detail = session.query(UserDetail).filter(UserDetail.id == username).first()
        if detail is None or detail.image is None:
            return StreamingResponse(open("default.png", "rb"))
    return StreamingResponse([detail.image.data])
