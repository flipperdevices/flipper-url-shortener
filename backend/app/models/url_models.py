from datetime import datetime

from sqlalchemy.sql import func
from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy import ForeignKey, DateTime, Integer, String

from app.core.utils.models_utils import BaseModel


class UrlModel(BaseModel):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(256), unique=True, index=True)
    original_url: Mapped[str] = mapped_column(String, index=True)

    tags = relationship(
        "TagModel", secondary="urls_tags", back_populates="urls", viewonly=True
    )
    visits: Mapped[int] = mapped_column(Integer, default=0)
    last_visit_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), server_onupdate=func.now()
    )


class UrlTagModel(BaseModel):
    __tablename__ = "urls_tags"

    url_id: Mapped[int] = mapped_column(
        ForeignKey("urls.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )
    tag = relationship("TagModel", foreign_keys=[tag_id])

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
