from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship

from app.core.db import Base


class Category(Base):
    __tablename__ = "category"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    kind = Column(String(20), nullable=False)
    parent_id = Column(BIGINT, ForeignKey("category.id"), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    deleted_at = Column(DateTime, nullable=True)

    parent = relationship("Category", remote_side=[id], backref="children")
