from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.schemas.transaction import (
    CategoryLiteral,
    TransactionCreateRequest,
    TransactionPatchRequest,
    TransactionRecord,
)
from app.services.ai_client import categorize_transaction
from app.store.memory_store import store

router = APIRouter(prefix="/v1/transactions", tags=["transactions"])


@router.post("", response_model=TransactionRecord, summary="Create a transaction")
def create_transaction(payload: TransactionCreateRequest) -> TransactionRecord:
    if payload.override_category is not None:
        return store.create_transaction(
            user_id=payload.user_id,
            description=payload.description,
            amount=payload.amount,
            currency=payload.currency,
            txn_date=payload.txn_date,
            merchant=None,
            predicted_category=payload.override_category,
            confidence=None,
            category_source="manual",
        )

    prediction = categorize_transaction(
        description=payload.description,
        amount=payload.amount,
        currency=payload.currency,
        txn_date=payload.txn_date.isoformat(),
    )
    return store.create_transaction(
        user_id=payload.user_id,
        description=payload.description,
        amount=payload.amount,
        currency=payload.currency,
        txn_date=payload.txn_date,
        merchant=prediction.merchant,
        predicted_category=prediction.category,
        confidence=prediction.confidence,
        category_source="ai",
    )


@router.get("", response_model=list[TransactionRecord], summary="List transactions")
def list_transactions(
    user_id: str = Query(..., min_length=1),
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    category: CategoryLiteral | None = Query(default=None),
) -> list[TransactionRecord]:
    if start and end and start > end:
        raise HTTPException(status_code=400, detail="start must be less than or equal to end")
    return store.list_transactions(user_id=user_id, start=start, end=end, category=category)


@router.patch("/{transaction_id}", response_model=TransactionRecord, summary="Override transaction category")
def patch_transaction(transaction_id: str, payload: TransactionPatchRequest) -> TransactionRecord:
    updated = store.update_category(transaction_id=transaction_id, override_category=payload.override_category)
    if updated is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return updated
