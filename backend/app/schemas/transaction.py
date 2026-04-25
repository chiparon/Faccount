from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, root_validator

from app.schemas.common import TransactionKind


class TransactionBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    transaction_type: TransactionKind
    occurred_at: datetime
    amount: Decimal = Field(..., gt=0)
    category_id: int
    from_account_id: Optional[int] = None
    to_account_id: Optional[int] = None
    note: Optional[str] = Field(default=None, max_length=255)


class TransactionCreate(TransactionBase):
    @root_validator
    def validate_account_links(cls, values):
        transaction_type = values.get("transaction_type")
        from_account_id = values.get("from_account_id")
        to_account_id = values.get("to_account_id")

        if transaction_type == TransactionKind.INCOME:
            if not to_account_id:
                raise ValueError("income transaction requires to_account_id")
        elif transaction_type == TransactionKind.EXPENSE:
            if not from_account_id:
                raise ValueError("expense transaction requires from_account_id")
        elif transaction_type == TransactionKind.TRANSFER:
            if not from_account_id or not to_account_id:
                raise ValueError("transfer transaction requires both account ids")
            if from_account_id == to_account_id:
                raise ValueError("transfer accounts must be different")
        return values


class TransactionRead(TransactionBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
