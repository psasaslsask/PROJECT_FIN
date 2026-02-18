# AI-Assisted Transaction Categorization Service (FastAPI)

Production-style FastAPI backend for QuickBooks-like transaction categorization using in-memory storage only.

## Tech Stack
- Python 3.11+
- FastAPI
- Pydantic v2
- Uvicorn
- In-memory, thread-safe storage (no database)

## Categories
Exactly supported categories:

```text
Income, Rent, Utilities, Groceries, Dining, Transportation, Travel, Entertainment, Shopping, Healthcare, Education, Subscriptions, Fees, Taxes, Other
```

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Run
```bash
uvicorn app.main:app --reload
```

Open API docs:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## API Endpoints

### 0) Service root (helpful for browser checks)
```bash
curl -s http://127.0.0.1:8000/
```

### 1) Health check
```bash
curl -s http://127.0.0.1:8000/health
```

### 2) Categorize only
```bash
curl -s -X POST http://127.0.0.1:8000/v1/categorize \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Uber trip downtown",
    "amount": 23.45,
    "currency": "USD",
    "txn_date": "2026-02-18"
  }'
```

### 3) Create transaction (auto AI/rules categorization)
```bash
curl -s -X POST http://127.0.0.1:8000/v1/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "description": "Netflix monthly charge",
    "amount": 14.99,
    "currency": "USD",
    "txn_date": "2026-02-18"
  }'
```

### 4) Create transaction (manual override)
```bash
curl -s -X POST http://127.0.0.1:8000/v1/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "description": "Custom expense",
    "amount": 88.00,
    "currency": "USD",
    "txn_date": "2026-02-17",
    "override_category": "Shopping"
  }'
```

### 5) List transactions
```bash
curl -s "http://127.0.0.1:8000/v1/transactions?user_id=user_123"
```

With filters:
```bash
curl -s "http://127.0.0.1:8000/v1/transactions?user_id=user_123&start=2026-02-01&end=2026-02-28&category=Subscriptions"
```

### 6) Patch transaction category override
```bash
curl -s -X PATCH http://127.0.0.1:8000/v1/transactions/<TRANSACTION_ID> \
  -H "Content-Type: application/json" \
  -d '{"override_category": "Travel"}'
```

## Demo Script (Interview-friendly: 3 commands)

1. Categorize one transaction:
```bash
curl -s -X POST http://127.0.0.1:8000/v1/categorize -H "Content-Type: application/json" -d '{"description":"Uber trip","amount":19.2,"currency":"USD","txn_date":"2026-02-18"}'
```

2. Create one stored transaction:
```bash
curl -s -X POST http://127.0.0.1:8000/v1/transactions -H "Content-Type: application/json" -d '{"user_id":"demo_user","description":"Starbucks coffee","amount":6.5,"currency":"USD","txn_date":"2026-02-18"}'
```

3. List stored transactions for that user:
```bash
curl -s "http://127.0.0.1:8000/v1/transactions?user_id=demo_user"
```

## Notes on AI Behavior
- If `OPENAI_API_KEY` is set, the service attempts an OpenAI-style chat completion call.
- If the key is missing, a deterministic mock AI is used.
- If AI fails or returns invalid output, the service falls back to rule-based categorization.
- Rule-based categorization handles known merchants/keywords and defaults to `Other` when unmatched.
