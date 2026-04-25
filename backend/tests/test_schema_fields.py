from app.schemas.account import AccountCreate
from app.schemas.category import CategoryCreate
from app.schemas.common import TransactionKind


def test_account_create_keeps_submitted_fields():
    payload = AccountCreate(name="微信零钱", type="purse")

    assert payload.name == "微信零钱"
    assert payload.type == "purse"


def test_category_create_keeps_submitted_name():
    payload = CategoryCreate(name="食物开销", kind=TransactionKind.EXPENSE)

    assert payload.name == "食物开销"
    assert payload.kind == TransactionKind.EXPENSE
