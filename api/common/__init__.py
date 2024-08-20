from fastapi import APIRouter
from fastapi.requests import Request
from sqlalchemy.orm import sessionmaker
from starlette.responses import StreamingResponse

from database.api import uploadImage
from database.db import engine
from database.table import Image
from utils.request import TokenRequest
from utils.response import Response
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


class GetImageRequest(TokenRequest):
    id: int


@router.post("/api/image/get")
async def getImage(request: GetImageRequest):
    username = resolveAccountJwt(request.token)["account"]
    session = sessionmaker(bind=engine)()
    with session:
        detail = session.query(Image).filter(Image.id == request.id).first()
        if not detail:
            return StreamingResponse(open("default.png", "rb"))
    return StreamingResponse([detail.data])
