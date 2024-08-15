from datetime import date
import typing

from fastapi import APIRouter
from pydantic import BaseModel

from database.api import *
from database.table import ImageType, ReportStatus
from utils.request import TokenRequest
from utils.response import Response
from utils import (resolveAccountJwt)
from pydantic import ConfigDict

router = APIRouter()


class UploadResponse(Response):
    fileId: str


# @router.post("/api/uploadImage")
# async def uploadImage(request: Request):
#     token = request.headers.get("token", None)
#     if token is None:
#         return Response(code=34, message="用户未登录")
#     username = resolveAccountJwt(token)["account"]
#     form = await request.form()
#     file = form.get("file")
#     fileFormat = file.filename.split(".")[-1]
#     id = f"{uuid.uuid1()}.{fileFormat}"
#     with open(f"images/{id}", "wb") as f:
#         f.write(await file.read())
#     return UploadResponse(code=0, message="", fileId=id)


class ReportRequest(BaseModel):
    token: str
    doctor: str
    images: typing.List[int]


@router.post("/api/submitReport")
async def submitReport(request: ReportRequest):
    session = sessionmaker(bind=engine)()
    username = resolveAccountJwt(request.token)["account"]
    with session:
        report = DenseReport(user=username, doctor=request.doctor)
        session.add(report)
        session.flush()
        for i in request.images:
            image = DenseImage(report=report.id, image=i, _type=ImageType.source)
            session.add(image)
        session.flush()
        session.commit()
        return Response()


class GetReportRequest(BaseModel):
    token: str


class Report(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    id: int
    user: str
    doctor: str
    submitTime: date
    current_status: ReportStatus


class ReportResponse(Response):
    reports: List[Report]


@router.post("/api/getReports")
async def getReports(request: GetReportRequest):
    username = resolveAccountJwt(request.token)["account"]
    session = sessionmaker(bind=engine)()
    with session:
        reports = get_reports(session, username)

        return ReportResponse(reports=[Report.model_validate(i) for i in reports])


class ReportImageRequest(TokenRequest):
    id: int
    type: ImageType


class ReportImageResponse(Response):
    images: List[int]


@router.post("/api/report/images")
def reportImages(request: ReportImageRequest):
    username = resolveAccountJwt(request.token)["account"]
    session = sessionmaker(bind=engine)()
    with session:
        results = session.query(DenseImage).join(DenseReport).filter(
            and_(DenseImage._type == request.type, DenseReport.id == request.id)).all()

        return ReportImageResponse(images=list([i.image for i in results]))
