from __future__ import annotations

from datetime import date, datetime
from threading import Lock
from uuid import uuid4

from app.schemas.transaction import CategoryLiteral, SourceLiteral, TransactionRecord


class MemoryStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._items: list[TransactionRecord] = []
        self._by_id: dict[str, TransactionRecord] = {}

    def create_transaction(
        self,
        user_id: str,
        description: str,
        amount: float,
        currency: str,
        txn_date: date,
        merchant: str | None,
        predicted_category: CategoryLiteral | None,
        confidence: float | None,
        category_source: SourceLiteral,
    ) -> TransactionRecord:
        record = TransactionRecord(
            id=str(uuid4()),
            user_id=user_id,
            description=description,
            amount=amount,
            currency=currency.upper(),
            txn_date=txn_date,
            merchant=merchant,
            predicted_category=predicted_category,
            confidence=confidence,
            category_source=category_source,
            created_at=datetime.utcnow(),
        )
        with self._lock:
            self._items.append(record)
            self._by_id[record.id] = record
        return record

    def list_transactions(
        self,
        user_id: str,
        start: date | None = None,
        end: date | None = None,
        category: CategoryLiteral | None = None,
    ) -> list[TransactionRecord]:
        with self._lock:
            snapshot = list(self._items)

        filtered = [item for item in snapshot if item.user_id == user_id]
        if start is not None:
            filtered = [item for item in filtered if item.txn_date >= start]
        if end is not None:
            filtered = [item for item in filtered if item.txn_date <= end]
        if category is not None:
            filtered = [item for item in filtered if item.predicted_category == category]

        return sorted(filtered, key=lambda x: (x.txn_date, x.created_at), reverse=True)

    def update_category(self, transaction_id: str, override_category: CategoryLiteral) -> TransactionRecord | None:
        with self._lock:
            existing = self._by_id.get(transaction_id)
            if existing is None:
                return None

            updated = existing.model_copy(
                update={
                    "predicted_category": override_category,
                    "category_source": "manual",
                    "confidence": None,
                }
            )

            self._by_id[transaction_id] = updated
            for idx, item in enumerate(self._items):
                if item.id == transaction_id:
                    self._items[idx] = updated
                    break

        return updated


store = MemoryStore()
