from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.mysql import BIGINT

from app.core.db import Base


class TransactionRecord(Base):
    __tablename__ = "transaction_record"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    transaction_type = Column(String(20), nullable=False)
    occurred_at = Column(DateTime, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    category_id = Column(BIGINT, ForeignKey("category.id"), nullable=False)
    from_account_id = Column(BIGINT, ForeignKey("account.id"), nullable=True)
    to_account_id = Column(BIGINT, ForeignKey("account.id"), nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

