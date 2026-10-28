# API Documentation

Base URL (local): `http://127.0.0.1:8000`

Interactive docs are also available at `/docs` (Swagger UI) and `/redoc`.

All request and response bodies are JSON. Successful responses return the resource directly (they are not wrapped in an envelope). Error responses use the format in [Error Format](#error-format).

**Note on Money Format:** Because this API uses Python `Decimal` for exact precision, all money values (`balance`, `amount`, `new_balance`) are returned as **JSON Strings** (e.g., `"100.00"`), not JSON Numbers. This prevents frontend clients from losing precision due to floating-point rounding.

## Endpoint Summary

| Purpose | Method | Path |
|---|---|---|
| Create account | POST | `/account/create` |
| Get balance | GET | `/account/{account_id}/balance` |
| Add transaction (credit / debit) | POST | `/transaction/self` |
| Get transaction history | GET | `/transaction/{account_id}/history` |
| Transfer money (bonus) | POST | `/transaction/account` |

---

## 1. Create Account
`POST /account/create`  →  **201 Created**

Request:
```json
{ "name": "Alice" }
```
- `name` is required, minimum 3 characters. Leading and trailing spaces are trimmed before saving, and a blank name (only spaces) is rejected with 422.
- Any other field in the body (for example `balance`) is ignored. The balance is never read from the client.

Response:
```json
{
  "id": "3f2b8c1e-....",
  "name": "Alice",
  "balance": 0.0,
  "created_at": "2026-10-28T13:30:00.123456Z"
}
```

| Situation | Status |
|---|---|
| Success | 201 |
| Missing, too short or blank name | 422 |

---

## 2. Add Transaction (credit / debit)
`POST /transaction/self`  →  **201 Created**

Request:
```json
{
  "account_id": "3f2b8c1e-....",
  "type": "credit",
  "amount": 100,
  "description": "Salary",
  "reference_id": "REF-0001"
}
```

| Field | Rule |
|---|---|
| `account_id` | valid UUID of an existing account |
| `type` | `"credit"` or `"debit"` |
| `amount` | greater than 0; handled as a `Decimal` and stored as `NUMERIC(15, 2)` |
| `reference_id` | required, minimum 5 characters, unique per account |
| `description` | optional |

Response:
```json
{
  "id": "…",
  "account_id": "…",
  "type": "credit",
  "amount": 100.0,
  "description": "Salary",
  "new_balance": 100.0,
  "reference_id": "REF-0001",
  "created_at": "…"
}
```

| Situation | Status |
|---|---|
| Success | 201 |
| Account does not exist | 404 |
| `reference_id` already used on this account | 409 (no new row, balance unchanged) |
| Debit larger than the balance | 400 (balance unchanged) |
| Invalid body, type, amount or UUID | 422 |

Rules:
- A credit increases the balance by `amount`; a debit decreases it by `amount`.
- A rejected or failed transaction never changes the balance.
- The same `reference_id` may be used on different accounts.

---

## 3. Get Account Balance
`GET /account/{account_id}/balance`  →  **200 OK**

Response:
```json
{ "account_id": "…", "balance": 70.0 }
```

| Situation | Status |
|---|---|
| Success | 200 |
| Account does not exist | 404 |
| `account_id` is not a valid UUID | 422 |

---

## 4. Get Transaction History
`GET /transaction/{account_id}/history?type=credit&page=1&limit=10`  →  **200 OK**

| Query param | Default | Rule |
|---|---|---|
| `type` | none (both types returned) | `credit` or `debit` |
| `page` | 1 | integer ≥ 1 |
| `limit` | 10 | integer from 1 to 50 |

Response:
```json
{
  "page": 1,
  "limit": 10,
  "total_records": 25,
  "total_pages": 3,
  "transactions": [
    {
      "id": "…",
      "account_id": "…",
      "type": "debit",
      "amount": 20.0,
      "description": null,
      "new_balance": null,
      "reference_id": "…",
      "created_at": "…"
    }
  ]
}
```

- Sorted by `created_at` descending, with `id` descending as a tie-breaker.
- `new_balance` is not stored per transaction, so it is `null` in history items.
- A page beyond the last page returns an empty `transactions` list.
- `total_pages` is `0` when there are no matching records.

| Situation | Status |
|---|---|
| Success | 200 |
| Account does not exist | 404 |
| Invalid `page`, `limit`, `type` or UUID | 422 |

---

## 5. Transfer Money (Bonus)
`POST /transaction/account`  →  **200 OK**

Request:
```json
{
  "from_account_id": "…",
  "to_account_id": "…",
  "amount": 30,
  "reference_id": "TRF-0001",
  "description": "Rent share"
}
```

| Field | Rule |
|---|---|
| `from_account_id`, `to_account_id` | valid UUIDs of existing, different accounts |
| `amount` | greater than 0; handled as a `Decimal` and stored as `NUMERIC(15, 2)` |
| `reference_id` | required, minimum 5 characters |
| `description` | optional |

Response:
```json
{
  "message": "Transfer successful",
  "reference_id": "TRF-0001",
  "from_account_id": "…",
  "to_account_id": "…",
  "amount": 30.0,
  "created_at": "…"
}
```

| Situation | Status |
|---|---|
| Success | 200 |
| Same source and destination | 400 |
| One or both accounts missing | 404 |
| `reference_id` already used on the source or the destination account | 409 |
| Insufficient balance in the source account | 400 |
| Invalid body | 422 |

A successful transfer writes **two** rows to `transactions`: a `debit` on the source account and a `credit` on the destination account. Both use the same `reference_id`, which is allowed because uniqueness is per account. The debit, the credit and both balance updates happen in one database transaction; if any step fails, nothing is saved. Because the debit and credit rows share the `reference_id`, the duplicate check covers both accounts: if either one already has a transaction with that `reference_id`, the transfer is rejected with 409 before anything is written.

---

## Error Format

Errors raised by the application (400, 404, 409, 422) use one shape:

```json
{
  "success": false,
  "message": "Account not found",
  "details": null
}
```

For validation errors (422), `message` is `"Validation Error"` and `details` holds the list of field errors, for example:

```json
{
  "success": false,
  "message": "Validation Error",
  "details": [
    { "type": "greater_than", "loc": ["body", "amount"], "msg": "Input should be greater than 0", "input": 0 }
  ]
}
```

### Status Code Summary

| Code | Meaning in this API |
|---|---|
| 200 | Success (balance, history, transfer) |
| 201 | Account or transaction created |
| 400 | Insufficient balance, or transfer to the same account |
| 404 | Account not found (or unknown URL) |
| 409 | Duplicate `reference_id` |
| 422 | Request validation failed |
| 503 | Database unavailable |
