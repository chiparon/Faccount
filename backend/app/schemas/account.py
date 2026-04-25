from datetime import datetime

from pydantic import BaseModel, constr


class AccountBase(BaseModel):
    name: constr(strip_whitespace=True, min_length=1, max_length=50)
    type: constr(strip_whitespace=True, min_length=1, max_length=30)


class AccountCreate(AccountBase):
    pass


class AccountRead(AccountBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
