from datetime import datetime

from fastapi import Body
from pydantic import BaseModel, HttpUrl, field_validator


class CreateUrlRequestSchema(BaseModel):
    slug: str = Body(..., min_length=1, max_length=256)
    original_url: HttpUrl

    @field_validator("original_url")
    @classmethod
    def convert_int_serial(cls, value: HttpUrl):
        return str(value)


class CreateUrlResponseSchema(BaseModel):
    id: int
    slug: str
    original_url: HttpUrl
    visits: int
    last_visit_at: datetime
    created_at: datetime
    updated_at: datetime


class AddTagUrlRequestSchema(BaseModel):
    tag_ids: list[int] = Body(...)


class AddTagUrlResponseSchema(BaseModel):
    id: int
    name: str


class ListUrlResponseSchema(BaseModel):
    id: int
    slug: str
    original_url: HttpUrl
    tags: list[AddTagUrlResponseSchema]
    visits: int
    last_visit_at: datetime
    created_at: datetime
    updated_at: datetime


class UpdateUrlRequestSchema(BaseModel):
    slug: str = Body(None, min_length=1, max_length=256)
    original_url: HttpUrl = Body(None)

    @field_validator("original_url")
    @classmethod
    def convert_int_serial(cls, value: HttpUrl):
        return str(value)
