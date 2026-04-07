# Python Backend (FastAPI + MongoDB)

This backend implements the domain and endpoint behavior described by `Blueprint.md` and `openapi.yaml`.

## Features

- Layered architecture: routes → controllers → services → repositories
- MongoDB persistence for users, products, orders
- JWT access token + refresh token lifecycle
- RBAC (auth/admin) and order ownership scoping
- Soft delete for users/products and hard delete for orders
- Cart summary and checkout (cart → order + cart clear)
- Uniform JSON response envelope
- Request id, security headers, basic rate limiting

## Setup

```bash
python -m pip install -r requirements.txt
cp .env.example .env
```

Set required values in `.env`:

- `MONGO_URI`
- `ACCESS_TOKEN_SECRET`
- `REFRESH_TOKEN_SECRET`

## Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 3000
```

## Tests

```bash
pytest -q
```
