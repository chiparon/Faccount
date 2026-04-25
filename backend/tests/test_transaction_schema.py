from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas.common import TransactionKind
from app.schemas.transaction import TransactionCreate


def base_payload():
    return {
        "title": "test",
        "transaction_type": TransactionKind.TRANSFER,
        "occurred_at": datetime(2026, 4, 24, 0, 0, 0),
        "amount": "10.00",
        "category_id": 1,
        "from_account_id": 1,
        "to_account_id": 2,
        "note": "demo",
    }


def test_transfer_requires_distinct_accounts():
    payload = base_payload()
    payload["to_account_id"] = 1

    with pytest.raises(ValidationError):
        TransactionCreate(**payload)


def test_income_requires_to_account():
    payload = base_payload()
    payload["transaction_type"] = TransactionKind.INCOME
    payload["from_account_id"] = None
    payload["to_account_id"] = None

    with pytest.raises(ValidationError):
        TransactionCreate(**payload)


def test_expense_requires_from_account():
    payload = base_payload()
    payload["transaction_type"] = TransactionKind.EXPENSE
    payload["from_account_id"] = None
    payload["to_account_id"] = None

    with pytest.raises(ValidationError):
        TransactionCreate(**payload)

