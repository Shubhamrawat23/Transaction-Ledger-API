from fastapi import FastAPI, Request, status, HTTPException
from modules.models.accounts.routes import account_routes
from modules.models.transaction.routes import transc_routes
from contextlib import asynccontextmanager
from modules.db.connection import db_pool
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


# pool open as the uvicorn start
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Connecting pool with DB....")
    db_pool.open()
    print("Pool connected with DB")
    yield
    print("Pool closed connection with DB")
    db_pool.close()

app = FastAPI(lifespan=lifespan)

app.include_router(account_routes, prefix="/account", tags=["Accounts"])
app.include_router(transc_routes, prefix="/transaction", tags=["Transactions"])


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation Error",
            "details": exc.errors()
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "details": None
        }
    )
