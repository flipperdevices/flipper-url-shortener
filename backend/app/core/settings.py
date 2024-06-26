from pydantic_settings import BaseSettings
from pydantic import Field


class BaseConfigSettings(BaseSettings):
    class Config:
        env_file = ".env"
        extra = "ignore"


class ApplicationSettings(BaseConfigSettings):
    APP_TITLE: str = Field("URL Shortener")
    APP_VERSION: str = Field("0.1.0")
    APP_DEBUG: bool = Field(False)
    APP_API_VERSION_STR: str = Field("v0")
    APP_OPENAPI_URL: str = Field("/api/openapi.json")

    POSTGRES_URL: str = Field()
    ROOT_REDIRECT_URL: str | None = Field(None)

    CACHE_ACTIVE: bool = Field(True)
    CACHE_EXPIRE_TIME: int = Field(999999999999)


application_settings = ApplicationSettings()
