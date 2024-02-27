from pydantic import Field
from pydantic_settings import BaseSettings


class BaseConfigSettings(BaseSettings):
    class Config:
        env_file = '.env'
        extra = 'ignore'


class ApplicationSettings(BaseConfigSettings):
    APP_TITLE: str = Field('URL Shortener')
    APP_VERSION: str = Field('0.1.0')
    APP_DEBUG: bool = Field(False)
    APP_API_VERSION_STR: str = Field('v0')

    APP_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(180)
    APP_SECRET_KEY: str = Field('SECRET KEY')

    FIRST_USER_USERNAME: str = Field('admin')
    FIRST_USER_PASSWORD: str = Field('admin')
    FIRST_USER_EMAIL: str = Field('admin@gmail.com')

    POSTGRES_URL: str = Field('postgresql+asyncpg://user:password@postgres/postgres')

    MEMCACHED_HOST: str = Field('localhost')
    MEMCACHED_PORT: int = Field(11211)
    CACHE_EXPIRE_TIME: int = Field(180)
    CACHE_ACTIVE: bool = Field(True)


application_settings = ApplicationSettings()
