from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class AccountCreate(BaseModel):
    owner_name: str = Field(min_length=3, max_length=100)
    balance: Decimal = Field(Decimal("0.0"))
    model_config = ConfigDict(from_attributes=True)


class BaseAccount(AccountCreate):
    id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
