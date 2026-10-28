from psycopg_pool import ConnectionPool, PoolTimeout
from psycopg import OperationalError
from psycopg.rows import dict_row
from fastapi import HTTPException
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

db_pool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=15,
    kwargs={"row_factory": dict_row}  #return data in dict instead of tuple
)

def get_connection():
    try:
        with db_pool.connection() as con:
            yield con
    except (PoolTimeout, OperationalError) as e:

        print(f"Database connection error: {e}")

        raise HTTPException(
            status_code=503,
            detail={
                "code":503,
                "success":False,
                "data":[],
                "error":"Database service is currently unavailable.",
            }
        )