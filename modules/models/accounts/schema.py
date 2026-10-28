from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from decimal import Decimal

class AccountCreation(BaseModel):
    name: str = Field(..., min_length=3)

class AccountResponse(BaseModel):
    id: UUID
    name: str
    balance: Decimal
    created_at: datetime

class AccountBalanceResponse(BaseModel):
    account_id: UUID
    balance: Decimal
