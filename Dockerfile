# pull official base image
FROM python:3.10.2-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ Asia/Tehran
RUN apt-get update && \
    apt-get install tzdata 
    # apt-get install nano

# set work directory
RUN mkdir /home/web
WORKDIR /home/web

# install dependencies
COPY web/requirements.txt /home/web/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
RUN pip install https://github.com/KurimuzonAkuma/pyrogram/archive/v2.1.22.zip --force-reinstall


# copy project
COPY . /home/


