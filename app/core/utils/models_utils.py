from app.core.postgres.db import Base
from sqlalchemy.ext.asyncio import AsyncAttrs


class BaseModel(AsyncAttrs, Base):
    __abstract__ = True
