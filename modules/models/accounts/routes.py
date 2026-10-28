from fastapi import APIRouter, status, Depends
import modules.models.accounts.schema as acc_schema
import modules.models.accounts.service as service
from psycopg import Connection
from modules.db.connection import get_connection
from uuid import UUID
 
account_routes = APIRouter()

@account_routes.post('/create', status_code=status.HTTP_201_CREATED, response_model=acc_schema.AccountResponse)
def create_account_route(acc_data: acc_schema.AccountCreation, db: Connection = Depends(get_connection)):
    result = service.create_account(db, acc_data)

    return result

@account_routes.get("/{account_id}/balance", response_model=acc_schema.AccountBalanceResponse)
def get_balance_route(account_id: UUID, db: Connection = Depends(get_connection)):
    return service.fetch_balance(db, account_id)