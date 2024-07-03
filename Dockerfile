# syntax=docker/dockerfile:1
# Based on https://docs.docker.com/language/python/containerize/

ARG PYTHON_VERSION=3.12.4
FROM python:${PYTHON_VERSION}-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

COPY . .

ENV SLIME_HOOK_CONFG=/config.yaml
CMD python3 cli.py $SLIME_HOOK_CONFG
