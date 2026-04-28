from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Account, Category, TransactionItem, TransactionRecord
from app.schemas import (
    AccountCreate,
    AccountRead,
    CategoryCreate,
    CategoryRead,
    TransactionCreate,
    TransactionRead,
    TransactionUpdate,
)


router = APIRouter()


def safe_commit(db: Session, conflict_message: str):
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=conflict_message) from exc


@router.get("/accounts", response_model=List[AccountRead])
def list_accounts(db: Session = Depends(get_db)):
    return db.query(Account).filter(Account.deleted_at.is_(None)).order_by(Account.id.desc()).all()


@router.post("/accounts", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
def create_account(payload: AccountCreate, db: Session = Depends(get_db)):
    exists = db.query(Account).filter(Account.name == payload.name, Account.deleted_at.is_(None)).first()
    if exists:
        raise HTTPException(status_code=400, detail="account name already exists")

    record = Account(**payload.dict())
    db.add(record)
    safe_commit(db, "account name is still used in Trash; restore or permanently delete it first")
    db.refresh(record)
    return record


@router.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    record = db.query(Account).filter(Account.id == account_id, Account.deleted_at.is_(None)).first()
    if not record:
        raise HTTPException(status_code=404, detail="account not found")

    record.deleted_at = datetime.utcnow()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/categories", response_model=List[CategoryRead])
def list_categories(db: Session = Depends(get_db)):
    return (
        db.query(Category)
        .filter(Category.deleted_at.is_(None))
        .order_by(Category.sort_order.asc(), Category.id.asc())
        .all()
    )


@router.post("/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    exists = db.query(Category).filter(Category.name == payload.name, Category.deleted_at.is_(None)).first()
    if exists:
        raise HTTPException(status_code=400, detail="category name already exists")

    if payload.parent_id:
        parent = db.query(Category).filter(Category.id == payload.parent_id, Category.deleted_at.is_(None)).first()
        if not parent:
            raise HTTPException(status_code=404, detail="parent category not found")
        if parent.kind != payload.kind:
            raise HTTPException(status_code=400, detail="parent and child kinds must match")

    record = Category(**payload.dict())
    db.add(record)
    safe_commit(db, "category name is still used in Trash; restore or permanently delete it first")
    db.refresh(record)
    return record


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    record = db.query(Category).filter(Category.id == category_id, Category.deleted_at.is_(None)).first()
    if not record:
        raise HTTPException(status_code=404, detail="category not found")

    record.deleted_at = datetime.utcnow()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/transactions", response_model=List[TransactionRead])
def list_transactions(
    start_at: Optional[datetime] = None,
    end_at: Optional[datetime] = None,
    transaction_type: Optional[str] = None,
    category_id: Optional[int] = None,
    account_id: Optional[int] = None,
    q: Optional[str] = None,
    amount_min: Optional[float] = None,
    amount_max: Optional[float] = None,
    sort_by: str = Query("occurred_at", regex="^(occurred_at|amount|created_at|id)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    query = db.query(TransactionRecord).filter(TransactionRecord.deleted_at.is_(None))

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
    if q:
        like_text = f"%{q}%"
        query = query.filter(
            (TransactionRecord.title.like(like_text))
            | (TransactionRecord.note.like(like_text))
            | (TransactionRecord.source_logic.like(like_text))
        )
    if amount_min is not None:
        query = query.filter(TransactionRecord.amount >= amount_min)
    if amount_max is not None:
        query = query.filter(TransactionRecord.amount <= amount_max)

    sort_column = getattr(TransactionRecord, sort_by)
    if sort_order == "asc":
        query = query.order_by(sort_column.asc(), TransactionRecord.id.asc())
    else:
        query = query.order_by(sort_column.desc(), TransactionRecord.id.desc())

    return query.all()


def validate_transaction_payload(payload: TransactionCreate, db: Session):
    category = db.query(Category).filter(Category.id == payload.category_id, Category.deleted_at.is_(None)).first()
    if not category:
        raise HTTPException(status_code=404, detail="category not found")

    if category.kind != payload.transaction_type.value:
        raise HTTPException(status_code=400, detail="transaction type and category kind mismatch")

    if payload.from_account_id:
        account = db.query(Account).filter(Account.id == payload.from_account_id, Account.deleted_at.is_(None)).first()
        if not account:
            raise HTTPException(status_code=404, detail="from account not found")

    if payload.to_account_id:
        account = db.query(Account).filter(Account.id == payload.to_account_id, Account.deleted_at.is_(None)).first()
        if not account:
            raise HTTPException(status_code=404, detail="to account not found")

    for item in payload.items:
        if item.category_id:
            item_category = (
                db.query(Category)
                .filter(Category.id == item.category_id, Category.deleted_at.is_(None))
                .first()
            )
            if not item_category:
                raise HTTPException(status_code=404, detail="transaction item category not found")


def apply_transaction_payload(record: TransactionRecord, payload: TransactionCreate):
    data = payload.dict()
    items = data.pop("items", [])
    for key, value in data.items():
        setattr(record, key, value)
    record.items = [TransactionItem(**item) for item in items]


@router.post(
    "/transactions",
    response_model=TransactionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    validate_transaction_payload(payload, db)
    record = TransactionRecord()
    apply_transaction_payload(record, payload)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.put("/transactions/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    db: Session = Depends(get_db),
):
    record = (
        db.query(TransactionRecord)
        .filter(TransactionRecord.id == transaction_id, TransactionRecord.deleted_at.is_(None))
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="transaction not found")

    validate_transaction_payload(payload, db)
    apply_transaction_payload(record, payload)
    record.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(record)
    return record


@router.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    record = (
        db.query(TransactionRecord)
        .filter(TransactionRecord.id == transaction_id, TransactionRecord.deleted_at.is_(None))
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="transaction not found")

    record.deleted_at = datetime.utcnow()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/trash")
def list_trash(
    entity_type: Optional[str] = Query(default=None, regex="^(account|category|transaction)$"),
    q: Optional[str] = None,
    db: Session = Depends(get_db),
):
    result = {}
    like_text = f"%{q}%" if q else None

    if entity_type in (None, "account"):
        query = db.query(Account).filter(Account.deleted_at.is_not(None))
        if like_text:
            query = query.filter((Account.name.like(like_text)) | (Account.type.like(like_text)))
        result["accounts"] = query.order_by(Account.deleted_at.desc()).all()

    if entity_type in (None, "category"):
        query = db.query(Category).filter(Category.deleted_at.is_not(None))
        if like_text:
            query = query.filter(Category.name.like(like_text))
        result["categories"] = query.order_by(Category.deleted_at.desc()).all()

    if entity_type in (None, "transaction"):
        query = db.query(TransactionRecord).filter(TransactionRecord.deleted_at.is_not(None))
        if like_text:
            query = query.filter(
                (TransactionRecord.title.like(like_text))
                | (TransactionRecord.note.like(like_text))
                | (TransactionRecord.source_logic.like(like_text))
            )
        result["transactions"] = query.order_by(TransactionRecord.deleted_at.desc()).all()

    return result


@router.post("/trash/{entity_type}/{record_id}/restore")
def restore_from_trash(entity_type: str, record_id: int, db: Session = Depends(get_db)):
    model_map = {
        "account": Account,
        "category": Category,
        "transaction": TransactionRecord,
    }
    model = model_map.get(entity_type)
    if not model:
        raise HTTPException(status_code=404, detail="trash entity type not found")

    record = db.query(model).filter(model.id == record_id, model.deleted_at.is_not(None)).first()
    if not record:
        raise HTTPException(status_code=404, detail="trash record not found")

    record.deleted_at = None
    safe_commit(db, "active record with same unique name already exists")
    return {"status": "restored", "entity_type": entity_type, "id": record_id}


def delete_transaction_permanently(record: TransactionRecord, db: Session):
    db.query(TransactionItem).filter(TransactionItem.transaction_id == record.id).delete()
    db.delete(record)


def delete_category_permanently(record: Category, db: Session):
    has_child = db.query(Category).filter(Category.parent_id == record.id).first()
    if has_child:
        raise HTTPException(status_code=409, detail="category has child categories")
    linked_transaction = db.query(TransactionRecord).filter(TransactionRecord.category_id == record.id).first()
    linked_item = db.query(TransactionItem).filter(TransactionItem.category_id == record.id).first()
    if linked_transaction or linked_item:
        raise HTTPException(status_code=409, detail="category is used by transactions or transaction items")
    db.delete(record)


def delete_account_permanently(record: Account, db: Session):
    linked_transaction = (
        db.query(TransactionRecord)
        .filter(
            or_(
                TransactionRecord.from_account_id == record.id,
                TransactionRecord.to_account_id == record.id,
            )
        )
        .first()
    )
    if linked_transaction:
        raise HTTPException(status_code=409, detail="account is used by transactions")
    db.delete(record)


@router.delete("/trash/{entity_type}/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def permanently_delete_trash_record(entity_type: str, record_id: int, db: Session = Depends(get_db)):
    if entity_type == "transaction":
        record = (
            db.query(TransactionRecord)
            .filter(TransactionRecord.id == record_id, TransactionRecord.deleted_at.is_not(None))
            .first()
        )
        if not record:
            raise HTTPException(status_code=404, detail="trash transaction not found")
        delete_transaction_permanently(record, db)
    elif entity_type == "category":
        record = db.query(Category).filter(Category.id == record_id, Category.deleted_at.is_not(None)).first()
        if not record:
            raise HTTPException(status_code=404, detail="trash category not found")
        delete_category_permanently(record, db)
    elif entity_type == "account":
        record = db.query(Account).filter(Account.id == record_id, Account.deleted_at.is_not(None)).first()
        if not record:
            raise HTTPException(status_code=404, detail="trash account not found")
        delete_account_permanently(record, db)
    else:
        raise HTTPException(status_code=404, detail="trash entity type not found")

    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/trash")
def clear_trash(
    entity_type: Optional[str] = Query(default=None, regex="^(account|category|transaction)$"),
    db: Session = Depends(get_db),
):
    deleted = {"transactions": 0, "categories": 0, "accounts": 0}
    skipped = []

    if entity_type in (None, "transaction"):
        for record in db.query(TransactionRecord).filter(TransactionRecord.deleted_at.is_not(None)).all():
            delete_transaction_permanently(record, db)
            deleted["transactions"] += 1
        db.flush()

    if entity_type in (None, "category"):
        categories = db.query(Category).filter(Category.deleted_at.is_not(None)).order_by(Category.id.desc()).all()
        for record in categories:
            try:
                delete_category_permanently(record, db)
                db.flush()
                deleted["categories"] += 1
            except HTTPException as exc:
                skipped.append({"entity_type": "category", "id": record.id, "name": record.name, "reason": exc.detail})

    if entity_type in (None, "account"):
        accounts = db.query(Account).filter(Account.deleted_at.is_not(None)).all()
        for record in accounts:
            try:
                delete_account_permanently(record, db)
                db.flush()
                deleted["accounts"] += 1
            except HTTPException as exc:
                skipped.append({"entity_type": "account", "id": record.id, "name": record.name, "reason": exc.detail})

    db.commit()
    return {"status": "cleared", "deleted": deleted, "skipped": skipped}
