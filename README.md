# About
This is a public repository of Flipper URL Shortener created using Python and Vue.js

### **THERE IS NO AUTHORIZATION OR OTHER SECURITY**

# Getting started

### Requirements
- Docker
- PostgresSQL

### Environment variables
Backend:
- APP_TITLE: string = URL Shortener
- APP_VERSION: string = 0.1.0
- APP_DEBUG: boolean = False
- APP_API_VERSION_STR: string = v0
- APP_OPENAPI_URL: string = /api/openapi.json **to disable API documentation set value to empty string \' \'**
- POSTGRES_URL: string = **REQUIRED**
- ROOT_REDIRECT_URL: string | None = None
- CACHE_ACTIVE: boolean = True
- CACHE_EXPIRE_TIME: int = 999999999999

Frontend:
- APP_PATH: string = /admin
- API_PATH: string = /api/v0/
- SHORTENED_URL_BASE_PATH: string = `${location.origin}/`

See `frontend/.env` for more description

### Start application
```
docker build -t test .
```

```
docker network create --driver host test
```

```
docker run --rm -d --name postgres --net=test -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password postgres:15.3-alpine
```

```
docker run --rm -it -p 8080:80 --net test -e POSTGRES_URL=postgresql+asyncpg://user:password@hostname/ test
```

Visit `http://127.0.0.1:8080/admin`

docker run --rm -d --name postgres --net=test -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=gO0ApG9C0kCfENco postgres:15.3-alpine

docker run --rm -it -p 8080:80 --net test -e POSTGRES_URL=postgresql+asyncpg://postgres:gO0ApG9C0kCfENco@postgres/ test

# Backend

### Main stack
- Python3.11
- FastAPI
- SQLAlchemy
- Alembic
- FastAPI-cache2
- FastAPI-pagination
- Uvicorn

### API Documentation
Visit `/api/docs#/` - **to disable API documentation set value to empty string \' \'**

### Security
There is no security, you have to protect your `/admin` and `/api` additionally

### Cache
**Only redirect router is cached**

As a cache backend we use `InMemoryBackend`, you can easily change it in the `backend/main.py`, see [package documentation](https://github.com/long2ice/fastapi-cache)

We have a custom `@cache_visits` decorator which works as usual but create a background task to increase visits count in the database

Also, we have a custom cache builder which creates a cache key from the request slug `{prefix}:{slug}`

Cache invalidation on short url update and delete by cache key
