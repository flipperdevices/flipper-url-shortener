FROM python:3.11-alpine

MAINTAINER devops@flipperdevices.com

COPY /pyproject.toml /poetry.lock /entrypoint.sh ./
RUN chmod +x /entrypoint.sh

COPY app /app

RUN apk add --no-cache curl gcc libffi-dev musl-dev

RUN pip install jsonschema==4.17.3 poetry && poetry config virtualenvs.create false && poetry install

ENV WORKERS=4
ENV HOST=0.0.0.0
ENV PORT=8000

EXPOSE ${PORT}/tcp

ENTRYPOINT ["/entrypoint.sh"]
