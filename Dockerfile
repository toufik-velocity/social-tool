FROM python:3.9-alpine3.13

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

WORKDIR /site

COPY requirements.txt requirements.txt

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r requirements.txt --index-url=https://pypi.python.org/simple/ && \
    adduser --disabled-password --no-create-home app

ENV PATH="/py/bin:$PATH"

USER app

COPY . .