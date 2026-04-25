from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Account, Category, TransactionRecord
from app.schemas import (
    AccountCreate,
    AccountRead,
    CategoryCreate,
    CategoryRead,
    TransactionCreate,
    TransactionRead,
)


router = APIRouter()


@router.get("/accounts", response_model=List[AccountRead])
def list_accounts(db: Session = Depends(get_db)):
    return db.query(Account).order_by(Account.id.desc()).all()


@router.post("/accounts", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
def create_account(payload: AccountCreate, db: Session = Depends(get_db)):
    exists = db.query(Account).filter(Account.name == payload.name).first()
    if exists:
        raise HTTPException(status_code=400, detail="account name already exists")

    record = Account(**payload.dict())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    record = db.query(Account).filter(Account.id == account_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="account not found")

    linked_transaction = (
        db.query(TransactionRecord)
        .filter(
            (TransactionRecord.from_account_id == account_id)
            | (TransactionRecord.to_account_id == account_id)
        )
        .first()
    )
    if linked_transaction:
        raise HTTPException(status_code=409, detail="account is used by transactions")

    db.delete(record)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/categories", response_model=List[CategoryRead])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.sort_order.asc(), Category.id.asc()).all()


@router.post("/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    exists = db.query(Category).filter(Category.name == payload.name).first()
    if exists:
        raise HTTPException(status_code=400, detail="category name already exists")

    if payload.parent_id:
        parent = db.query(Category).filter(Category.id == payload.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="parent category not found")
        if parent.kind != payload.kind:
            raise HTTPException(status_code=400, detail="parent and child kinds must match")

    record = Category(**payload.dict())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    record = db.query(Category).filter(Category.id == category_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="category not found")

    child = db.query(Category).filter(Category.parent_id == category_id).first()
    if child:
        raise HTTPException(status_code=409, detail="category has child categories")

    linked_transaction = (
        db.query(TransactionRecord)
        .filter(TransactionRecord.category_id == category_id)
        .first()
    )
    if linked_transaction:
        raise HTTPException(status_code=409, detail="category is used by transactions")

    db.delete(record)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/transactions", response_model=List[TransactionRead])
def list_transactions(
    start_at: Optional[datetime] = None,
    end_at: Optional[datetime] = None,
    transaction_type: Optional[str] = None,
    category_id: Optional[int] = None,
    account_id: Optional[int] = None,
    sort_by: str = Query("occurred_at", regex="^(occurred_at|amount|created_at|id)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    query = db.query(TransactionRecord)

    if start_at:
        query = query.filter(TransactionRecord.occurred_at >= start_at)
    if end_at:
        query = query.filter(TransactionRecord.occurred_at <= end_at)
    if transaction_type:
        query = query.filter(TransactionRecord.transaction_type == transaction_type)
    if category_id:
        query = query.filter(TransactionRecord.category_id == category_id)
    if account_id:
        query = query.filter(
            (TransactionRecord.from_account_id == account_id)
            | (TransactionRecord.to_account_id == account_id)
        )

    sort_column = getattr(TransactionRecord, sort_by)
    if sort_order == "asc":
        query = query.order_by(sort_column.asc(), TransactionRecord.id.asc())
    else:
        query = query.order_by(sort_column.desc(), TransactionRecord.id.desc())

    return query.all()


@router.post(
    "/transactions",
    response_model=TransactionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == payload.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="category not found")

    if category.kind != payload.transaction_type.value:
        raise HTTPException(status_code=400, detail="transaction type and category kind mismatch")

    if payload.from_account_id:
        account = db.query(Account).filter(Account.id == payload.from_account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="from account not found")

    if payload.to_account_id:
        account = db.query(Account).filter(Account.id == payload.to_account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="to account not found")

    record = TransactionRecord(**payload.dict())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    record = db.query(TransactionRecord).filter(TransactionRecord.id == transaction_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="transaction not found")

    db.delete(record)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
