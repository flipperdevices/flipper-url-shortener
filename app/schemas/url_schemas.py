from datetime import datetime

from fastapi import Body
from pydantic import BaseModel, HttpUrl, field_validator


class CreateURLRequestSchema(BaseModel):
    domain: str = Body(..., min_length=1)
    slug: str = Body(..., min_length=1)
    original_url: HttpUrl

    @field_validator('original_url')
    @classmethod
    def convert_int_serial(cls, value: HttpUrl):
        return str(value)


class ListURLResponseSchema(BaseModel):
    id: int
    domain: str
    slug: str
    short_url: HttpUrl
    original_url: HttpUrl
    visits: int
    last_visit_at: datetime
    created_at: datetime
    updated_at: datetime


class UpdateURLRequestSchema(BaseModel):
    domain: str = Body(None, min_length=1)
    slug: str = Body(None, min_length=1)
    original_url: HttpUrl = Body(None)

    @field_validator('original_url')
    @classmethod
    def convert_int_serial(cls, value: HttpUrl):
        return str(value)
