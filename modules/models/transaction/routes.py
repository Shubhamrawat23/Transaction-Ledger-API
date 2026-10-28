from fastapi import APIRouter, status, Depends, Query
import modules.models.transaction.schema as transc_schema
from psycopg import Connection
from modules.db.connection import get_connection
import modules.models.transaction.service as transc_service
from typing import Optional, Literal
from uuid import UUID


transc_routes = APIRouter()

@transc_routes.post("/self", response_model=transc_schema.TransactionResponse, status_code=status.HTTP_201_CREATED)
def self_transaction_route(transc_data: transc_schema.TransactionCreate, db: Connection = Depends(get_connection)):
    return transc_service.self_transaction(db, transc_data)

@transc_routes.get("/{account_id}/history", response_model=transc_schema.TransactionHistoryResponse)
def history_route(account_id: UUID, type_filter: Optional[Literal["credit", "debit"]] = Query(None, alias="type"), page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=50), db: Connection = Depends(get_connection)):

    return transc_service.get_transaction_history(db, account_id, page, limit, type_filter)

@transc_routes.post("/account", response_model=transc_schema.AmtTransferResponse, status_code=status.HTTP_200_OK)
def transfer_route(transc_data: transc_schema.AmtTransferCreate, db: Connection = Depends(get_connection)):
    return transc_service.transfer_amount(db, transc_data)