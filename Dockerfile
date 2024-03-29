FROM python:3.7-alpine
MAINTAINER Antonin Marzelle Viroflay

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
# permet de ne pas avoir de dependencies en doublont
# - apk: nom du package issu de 3.7 alpine
# - --update: mettre a jours les éléments existants
# - --no-cache: supp les index
RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
        gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
RUN pip3 install -r /requirements.txt
RUN apk del .tmp-build-deps

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN adduser -D user
RUN chown -R user:user /vol/ 
RUN chmod -R 755 /vol/ 
USER user
