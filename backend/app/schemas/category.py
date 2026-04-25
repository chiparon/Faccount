from datetime import datetime
from typing import Optional

from pydantic import BaseModel, constr, root_validator

from app.schemas.common import TransactionKind


class CategoryBase(BaseModel):
    name: constr(strip_whitespace=True, min_length=1, max_length=50)
    kind: TransactionKind
    parent_id: Optional[int] = None
    is_active: bool = True
    sort_order: int = 0


class CategoryCreate(CategoryBase):
    @root_validator
    def validate_parent_link(cls, values):
        parent_id = values.get("parent_id")
        if parent_id is not None and parent_id <= 0:
            raise ValueError("parent_id must be positive")
        return values


class CategoryRead(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
