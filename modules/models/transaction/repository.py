from psycopg import Connection
from decimal import Decimal

def get_account(db: Connection, id: str):
    cur = db.execute("SELECT id, balance FROM accounts WHERE id = %s FOR UPDATE;",(id,))

    return cur.fetchone()

def check_duplicate_ref(db: Connection, acc_id: str, ref_id:str):
    cur = db.execute("SELECT id FROM transactions WHERE account_id = %s AND reference_id = %s;",(acc_id, ref_id))

    return cur.fetchone() is not None

def add_transaction(db: Connection, acc_id: str, type: str, amount: Decimal, ref_id: str,description: str = None):
    cur = db.execute("INSERT INTO TRANSACTIONS (account_id, type, amount, reference_id, description) VALUES (%s, %s, %s, %s, %s) RETURNING id, account_id, type, amount, description, reference_id, created_at;", (acc_id, type, amount, ref_id, description))

    return cur.fetchone()

def update_balance(db: Connection, acc_id: str, new_balance: Decimal):
    cur = db.execute("UPDATE accounts SET balance = %s WHERE id = %s RETURNING id;",(new_balance, acc_id))

    return cur.fetchone()


def check_account_exists(db: Connection, acc_id: str):
    cur = db.execute("SELECT id FROM accounts WHERE id = %s;", (acc_id,))
    return cur.fetchone() is not None

def count_transc(db: Connection, acc_id:str, type_filter: str = None):
    query = "SELECT COUNT(*) FROM transactions WHERE"
    params = []

    if type_filter:
        query += " type = %s AND"
        params.append(type_filter)

    query += " account_id = %s;"
    params.append(acc_id)

    cur = db.execute(query, tuple(params))

    return cur.fetchone()['count']

def fetch_transac(db: Connection, acc_id: str, offset: int = 0, limit: int = 10, type_filter: str = None):
    query = "SELECT id, account_id, type, amount, description, reference_id, created_at FROM transactions WHERE account_id = %s"
    params = [acc_id]

    if type_filter:
        query += " AND type = %s"
        params.append(type_filter)

    query += " ORDER BY created_at DESC, id DESC LIMIT %s OFFSET %s;"
    params.extend([limit, offset])

    cur = db.execute(query, tuple(params))

    return cur.fetchall()

def check_duplicate_ref_for_transfer(db: Connection, from_acc_id: str, to_acc_id: str, ref_id: str):
    cur = db.execute("SELECT id FROM transactions WHERE reference_id = %s AND account_id IN (%s, %s);", (ref_id, from_acc_id, to_acc_id))
    return cur.fetchone() is not None

def get_acc_for_update(db: Connection, account_ids: list):
    cur = db.execute("SELECT id, balance FROM accounts WHERE id = ANY(%s) ORDER BY id ASC FOR UPDATE;", (account_ids,)) # help in lock the 1st id in any transaction
    return cur.fetchall()