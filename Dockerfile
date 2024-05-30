FROM node:18-alpine3.19 AS frontend_builder
ADD frontend /app_src
WORKDIR /app_src
RUN npm i
RUN npm run build

FROM python:3.11-alpine
LABEL org.opencontainers.image.source=https://github.com/flipperdevices/flipper-url-shortener
MAINTAINER devops@flipperdevices.com
RUN apk add --no-cache curl gcc libffi-dev musl-dev
RUN apk add --no-cache curl
COPY backend/pyproject.toml backend/poetry.lock /app/
WORKDIR /app
RUN pip install jsonschema==4.17.3 poetry && poetry config virtualenvs.create false && poetry install
COPY backend/app /app/app
COPY backend/entrypoint.sh /app/
COPY --from=frontend_builder /app_src/dist/spa /app/static
ENV WORKERS=1
ENV HOST=0.0.0.0
ENV PORT=80
EXPOSE ${PORT}/tcp
CMD ["/app/entrypoint.sh"]
