from sqlalchemy.ext.asyncio import AsyncAttrs

from app.core.postgres.db import Base


class BaseModel(AsyncAttrs, Base):
    __abstract__ = True
