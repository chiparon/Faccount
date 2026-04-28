from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from app.api.routes import router
from app.core.db import Base, engine
from app.models import Account, Category, TransactionItem, TransactionRecord


def ensure_runtime_schema() -> None:
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    column_specs = {
        "account": {
            "deleted_at": "DATETIME NULL",
        },
        "category": {
            "deleted_at": "DATETIME NULL",
        },
        "transaction_record": {
            "source_logic": "VARCHAR(100) NULL",
            "updated_at": "DATETIME NULL",
            "deleted_at": "DATETIME NULL",
        },
    }

    with engine.begin() as connection:
        for table_name, specs in column_specs.items():
            existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
            for column_name, ddl in specs.items():
                if column_name not in existing_columns:
                    connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {ddl}"))


app = FastAPI(title="Accounts App API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.on_event("startup")
def startup() -> None:
    ensure_runtime_schema()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
