from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.requests import Request
from sqlalchemy.orm import sessionmaker

from database.api import uploadImage
from database.db import engine
from response import Response
from utils import resolveAccountJwt

router = APIRouter()


class ImageResponse(Response):
    image: int


@router.post("/api/image")
async def image(request: Request):
    form = await request.form()
    file = form.get("file")
    token = request.headers.get("token", default=None)
    if token is None:
        return Response(code=34, message="权限不足")
    username = resolveAccountJwt(token)['account']
    session = sessionmaker(bind=engine)()
    with session:
        return ImageResponse(image=uploadImage(session, file.filename, await file.read()))
