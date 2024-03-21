from datetime import datetime

from app.core.utils.models_utils import BaseModel
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


class URLModel(BaseModel):
    __tablename__ = 'urls'

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String, unique=True, index=True)
    original_url: Mapped[str] = mapped_column(String, index=True)

    visits: Mapped[int] = mapped_column(Integer, default=0)
    last_visit_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), server_onupdate=func.now())
