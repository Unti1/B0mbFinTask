
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class TransactionCreate(BaseModel):
    from_account: str
    to_account: str
    amount: Decimal = Field(..., ge=1)
    model_config = ConfigDict(from_attributes=True)
    
class BaseTransaction(TransactionCreate):
    id: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)