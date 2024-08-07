import os
import pathlib
import uuid
from typing import Any, List

from fastapi import APIRouter, UploadFile, Request
from pydantic import BaseModel

from database.api import *
from response import Response
from utils import (resolveAccountJwt)
from fastapi.responses import StreamingResponse

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
    fileId: str


@router.post("/api/submitReport")
async def submitReport(request: ReportRequest):
    Session = sessionmaker(bind=engine)
    session = Session()
    username = resolveAccountJwt(request.token)["account"]
    with session:
        report = addReport(session, username, request.doctor, request.fileId)
        return Response()


class GetReportRequest(BaseModel):
    token: str


class Report(BaseModel):
    id: int
    user: str
    doctor: str
    image: str
    submitTime: str
    current_status: str


class ReportResponse(Response):
    reports: List[Report]


@router.post("/api/getReports")
async def getReports(request: GetReportRequest):
    username = resolveAccountJwt(request.token)["account"]
    Session = sessionmaker(bind=engine)
    session = Session()
    with session:
        reports = get_reports(session, username)

        return ReportResponse(reports=list(map(
            lambda x: Report(id=x.id, user=x.user, doctor=x.doctor, image=x.image, submitTime=x.submitTime.strftime("%Y-%m-%d"),
                             current_status=x.current_status), reports)))


@router.post("/api/getReport")
async def getReports(request):
    pass
