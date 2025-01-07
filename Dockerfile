FROM python:3.12.4-slim
LABEL maintainer="vetali5700@gmail.com"

ENV PYTHOUNNBUFFERED=1

WORKDIR app/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
RUN mkdir -p /media/uploads/productphoto

RUN adduser \
    --disabled-password \
    --no-create-home \
    django_user

RUN chown -R django_user /media/uploads/productphoto
RUN chmod -R 755 /media/uploads/productphoto

USER django_user
