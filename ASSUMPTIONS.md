# Assumptions and Known Limitations

## Assumptions

The assignment does not specify these points, so the following choices were made.

### Accounts
1. **Single currency.** There is no currency field.
2. **Accounts cannot be deleted.** No delete endpoint exists, and the database blocks removal of an account that has transactions (`ON DELETE RESTRICT`).
3. **The balance never goes negative.** An account starts at 0, so a debit on an empty account is rejected. This is enforced in the service and by a database `CHECK (balance >= 0)`.
4. **Account name** must be at least 3 characters. Leading and trailing spaces are trimmed before saving, and a blank name (only spaces) is rejected with 422.

### Money
5. **Decimal arithmetic.** Amounts and balances are handled as Python `Decimal` and stored as `NUMERIC(15, 2)`: two decimal places, up to 13 digits before the decimal point. This avoids floating-point rounding errors.
6. **JSON String Serialization:** To prevent precision loss in frontend clients (like JavaScript, which uses binary floats), Pydantic v2 serializes all `Decimal` values as JSON Strings (e.g., `"balance": "10.50"`). 
7. **Decimal Places:** Because the database column is `NUMERIC(15, 2)`, if a client sends an amount with more than 2 decimal places (e.g., `10.555`), PostgreSQL will silently round it to 2 decimal places (`10.56`).

### Transactions
8. **`reference_id`** must be at least 5 characters. It is required for both transactions and transfers.
9. **`description`** is optional.
10. **Amount** must be greater than 0.
11. **Transaction `type`** values are lowercase: `credit` and `debit`.
12. **Duplicate `reference_id`** returns 409 with an error message. It does not replay or return the original transaction.
13. **Insufficient balance** returns 400.

### Transfers
14. A transfer requires a `reference_id`.
15. A transfer to the same account is rejected.
16. A transfer creates one debit row on the source account and one credit row on the destination account, both with the same `reference_id`.
17. The duplicate check for a transfer covers both the source and the destination account. A transfer is rejected with 409 if either account already has a transaction with that `reference_id`.

### History
18. Pagination defaults to page 1 and limit 10, with a maximum limit of 50.
19. An unknown account returns 404.
20. A page beyond the last page returns an empty list rather than an error.

### General
21. **Timestamps** come from PostgreSQL `CURRENT_TIMESTAMP` and are stored as `TIMESTAMPTZ`.
22. **No authentication or authorisation.** Anyone who can reach the API can use any account.
23. **Transaction immutability** is achieved by not exposing update or delete endpoints. There are no database triggers or permission restrictions behind it.
24. **Database:** PostgreSQL 18 or newer.

---

## Known Limitations

These reflect the current code and are listed so nothing is overstated.

### 1. Framework-level errors
An unknown URL returns 404, but its body is not confirmed to use the custom error format, because the custom handler is registered for FastAPI's `HTTPException` rather than the lower-level Starlette one.

### 2. 503 response shape
The "database unavailable" error passes an object as `detail`, so `message` is an object in that response instead of a string.

### 3. Not included
- Automated tests
- Docker setup
- Seed script
