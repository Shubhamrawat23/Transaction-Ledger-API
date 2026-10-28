from psycopg import Connection

def insert_account(db: Connection, name: str):
    query = """
        INSERT INTO accounts (name) 
        VALUES (%s) 
        RETURNING id, name, balance, created_at;
    """
    cursor = db.execute(query, (name,))
    return cursor.fetchone()

def get_account_balance(db: Connection, acc_id: str):
    query = "SELECT id as account_id, balance, created_at FROM accounts WHERE id = %s;"
    cur = db.execute(query, (acc_id,))
    return cur.fetchone()