from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.dialects.mysql import BIGINT

from app.core.db import Base


class Account(Base):
    __tablename__ = "account"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    type = Column(String(30), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    deleted_at = Column(DateTime, nullable=True)
