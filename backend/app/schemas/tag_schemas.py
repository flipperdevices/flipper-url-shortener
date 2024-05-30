from datetime import datetime

from fastapi import Body
from pydantic import BaseModel


class CreateTagRequestSchema(BaseModel):
    name: str = Body(..., min_length=1, max_length=150)


class CreateTagResponseSchema(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime


class ListTagResponseSchema(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime


class UpdateTagRequestSchema(BaseModel):
    name: str = Body(..., min_length=1, max_length=150)
