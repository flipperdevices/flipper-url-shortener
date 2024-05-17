FROM python:3.11-alpine

RUN apk add --no-cache curl

COPY pyproject.toml poetry.lock /app/
WORKDIR /app

RUN pip install jsonschema==4.17.3 poetry && poetry config virtualenvs.create false && poetry install

COPY app /app/app
COPY entrypoint.sh /app/

MAINTAINER devops@flipperdevices.com
ENV WORKERS=1
ENV HOST=0.0.0.0
ENV PORT=80

EXPOSE ${PORT}/tcp

CMD ["/app/entrypoint.sh"]
