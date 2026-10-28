from psycopg import Connection
import modules.models.accounts.repository as repository
from fastapi import HTTPException, status

def create_account(db : Connection,data):
    name = (data.name).strip()
    if not name or len(name) < 3: 
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Name must be at least 3 characters long after trimming spaces."
        )
    resp = repository.insert_account(db, name)
    return resp

def fetch_balance(db: Connection, acc_id: str):
    account = repository.get_account_balance(db, acc_id)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
        
    return account