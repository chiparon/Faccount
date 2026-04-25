from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
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


@router.get("/transactions", response_model=List[TransactionRead])
def list_transactions(db: Session = Depends(get_db)):
    return db.query(TransactionRecord).order_by(TransactionRecord.occurred_at.desc()).all()


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
