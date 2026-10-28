from psycopg import Connection
import modules.models.transaction.repository as repository
from fastapi import HTTPException, status
import math

def self_transaction(db: Connection, data):

    account = repository.get_account(db, data.account_id)

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )

    curr_balnace = account['balance']

    if repository.check_duplicate_ref(db, data.account_id, data.reference_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Transaction with reference_id '{data.reference_id}' already exists."
        )


    if data.type == "debit" and curr_balnace < data.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Insufficient balance for this debit transaction."
        )

    if data.type == "credit":
        new_balance = curr_balnace + data.amount
    else:
        new_balance = curr_balnace - data.amount

    transaction = repository.add_transaction(db, str(data.account_id), data.type, data.amount, data.reference_id, data.description)

    update_acc_id = repository.update_balance(db, str(data.account_id), new_balance)

    if update_acc_id:
        transaction['new_balance'] = new_balance

    return transaction

def get_transaction_history(db: Connection, acc_id: str, page: int, limit: int, type_filter: str = None):

    if not repository.check_account_exists(db, acc_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )

    offset = (page - 1) * limit
    total_pages = 0

    total_records = repository.count_transc(db, acc_id, type_filter)

    transactions = repository.fetch_transac(db, acc_id, offset, limit, type_filter)
    
    if total_records > 0:
        total_pages = math.ceil(total_records/limit)

    return {
        "page": page,
        "limit": limit,
        "total_records": total_records,
        "total_pages": total_pages,
        "transactions": transactions
    }

def transfer_amount(db: Connection, data):
    if data.from_account_id == data.to_account_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Cannot transfer to the same account"
            )

    # get both accounts balance
    accounts = repository.get_acc_for_update(db, [str(data.from_account_id), str(data.to_account_id)])

    if len(accounts) != 2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="One or both accounts not found"
            )

    acc_map_balance = {str(acc["id"]): acc['balance'] for acc in accounts}

    from_balance = acc_map_balance.get(str(data.from_account_id))
    to_balance = acc_map_balance.get(str(data.to_account_id))

    # check duplicate reference
    if repository.check_duplicate_ref_for_transfer(db, str(data.from_account_id), str(data.to_account_id), data.reference_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Transfer with this reference_id already processed for one of the accounts."
        )
    
    if from_balance < data.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance for transfer"
        )

    new_from_balance = from_balance - data.amount
    new_to_balance = to_balance + data.amount


    # add transactions and update balance in accounts
    from_transac = repository.add_transaction(
        db, str(data.from_account_id), "debit", data.amount, data.reference_id, data.description
    )
    from_balance_update = repository.update_balance(db, str(data.from_account_id), new_from_balance)

    to_transac = repository.add_transaction(
        db, str(data.to_account_id), "credit", data.amount, data.reference_id, data.description
    )
    to_balance_update = repository.update_balance(db, str(data.to_account_id), new_to_balance)

    return {
        "message": "Transfer successful",
        "reference_id": data.reference_id,
        "from_account_id": data.from_account_id,
        "to_account_id": data.to_account_id,
        "amount": data.amount,
        "from_account_new_balance": new_from_balance,
        "to_account_new_balance": new_to_balance,
        "created_at": from_transac['created_at']
    }
