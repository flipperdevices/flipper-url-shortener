from datetime import datetime

from app.core.utils.models_utils import BaseModel
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class TagModel(BaseModel):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, index=True, )
    urls = relationship(
        'UrlModel',
        secondary='urls_tags',
        back_populates='tags',
        viewonly=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), server_onupdate=func.now()
    )
