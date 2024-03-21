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

    POSTGRES_URL: str = Field('postgresql+asyncpg://user:password@postgres/postgres')

    CACHE_ACTIVE: bool = Field(True)


application_settings = ApplicationSettings()
