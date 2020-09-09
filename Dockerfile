FROM python:3.7-slim-stretch
ARG DJANGO_SETTINGS_MODULE
RUN echo ${DJANGO_SETTINGS_MODULE}

ENV PYTHONUNBUFFERED 1
MAINTAINER LinhLD <leduylinh209@gmail.com>

# Supervisor for Python & libaio1 for Oracle
RUN apt-get update && apt-get install -y supervisor && apt-get install -y --no-install-recommends g++ && rm -rf /var/lib/apt/lists/*

# Install python lib dep
COPY requirements/base.txt ./
RUN pip3 install -r base.txt
RUN pip3 install gunicorn
RUN apt-get purge -y --auto-remove g++

# Add code folder
RUN mkdir /code
WORKDIR /code
ADD . /code/

# Supervisor configuration
COPY deploy/supervisor_docker.conf /etc/supervisor/conf.d/supervisor_docker.conf

# Set Djanbgo env
ENV DJANGO_SETTINGS_MODULE ${DJANGO_SETTINGS_MODULE}

# create unprivileged user
RUN adduser --disabled-password --gecos '' myuser

EXPOSE 8888

ENTRYPOINT ["/code/entrypoint.sh"]