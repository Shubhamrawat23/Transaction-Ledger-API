from pydantic import BaseModel, Field
from typing import Literal, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal

class TransactionCreate(BaseModel):
    account_id: UUID
    amount: Decimal = Field(..., gt=0.00, description="Amount must be greater than 0")
    type: Literal["credit", "debit"]
    description: str | None = None
    reference_id: str = Field(..., min_length=5, description="Unique per account")


class TransactionResponse(BaseModel):
    id: UUID
    account_id: UUID
    type: str
    amount: Decimal
    description: str | None = None
    new_balance: Decimal | None = None
    reference_id: str
    created_at: datetime

class TransactionHistoryResponse(BaseModel):
    page: int
    limit: int
    total_records: int
    total_pages: int
    transactions: List[TransactionResponse]

class AmtTransferCreate(BaseModel):
    from_account_id: UUID
    to_account_id: UUID
    amount: Decimal = Field(..., gt=0.00, description="Amount must be greater than 0")
    reference_id: str = Field(..., min_length=5, description="Idempotency key")
    description: str | None = None

class AmtTransferResponse(BaseModel):
    message: str
    reference_id: str
    from_account_id: UUID
    to_account_id: UUID
    amount: Decimal
    created_at: datetime