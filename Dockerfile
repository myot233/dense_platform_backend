FROM dockerproxy.cn/python:latest
LABEL authors="myot233"

COPY ./ /dense_platform_backend
WORKDIR /dense_platform_backend
RUN pip3 install -r ./requirements.txt
CMD uvicorn main:app --host 0.0.0.0

