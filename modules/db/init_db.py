from modules.db.connection import db_pool

query = """

    CREATE TABLE IF NOT EXISTS accounts (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name TEXT NOT NULL CHECK (trim(name) <> ''),
        balance NUMERIC(15, 2) NOT NULL DEFAULT 0.00 CHECK (balance >=0),
        created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS transactions(
        id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
        account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
        type TEXT NOT NULL CHECK (type IN ('credit', 'debit')),
        amount NUMERIC(15, 2) NOT NULL CHECK (amount > 0),
        description TEXT,
        reference_id TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

        CONSTRAINT unique_account_reference_id UNIQUE (account_id, reference_id)
    );
"""

def init_db():
    try:
        with db_pool.connection() as conn:
            conn.execute(query)

        print("All tables created")
    finally:
        db_pool.close()


if __name__ == "__main__":
    init_db()

