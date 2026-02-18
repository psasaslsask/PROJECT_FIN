from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

CATEGORIES: list[str] = [
    "Income",
    "Rent",
    "Utilities",
    "Groceries",
    "Dining",
    "Transportation",
    "Travel",
    "Entertainment",
    "Shopping",
    "Healthcare",
    "Education",
    "Subscriptions",
    "Fees",
    "Taxes",
    "Other",
]

CategoryLiteral = Literal[
    "Income",
    "Rent",
    "Utilities",
    "Groceries",
    "Dining",
    "Transportation",
    "Travel",
    "Entertainment",
    "Shopping",
    "Healthcare",
    "Education",
    "Subscriptions",
    "Fees",
    "Taxes",
    "Other",
]

SourceLiteral = Literal["ai", "manual"]


class CategorizeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str = Field(..., min_length=1, examples=["Uber trip downtown"])
    amount: float = Field(..., examples=[23.45])
    currency: str = Field(default="USD", min_length=3, max_length=3, examples=["USD"])
    txn_date: date = Field(..., examples=["2026-02-18"])


class CategorizeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    merchant: str | None = Field(default=None, examples=["Uber"])
    category: CategoryLiteral = Field(..., examples=["Transportation"])
    confidence: float = Field(..., ge=0, le=1, examples=[0.93])
    reason: str = Field(..., min_length=3, examples=["Matched transportation keyword 'uber'."])


class TransactionCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str = Field(..., min_length=1, examples=["user_123"])
    description: str = Field(..., min_length=1, examples=["Netflix monthly subscription"])
    amount: float = Field(..., examples=[14.99])
    currency: str = Field(default="USD", min_length=3, max_length=3, examples=["USD"])
    txn_date: date = Field(..., examples=["2026-02-18"])
    override_category: CategoryLiteral | None = Field(default=None, examples=["Subscriptions"])


class TransactionPatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    override_category: CategoryLiteral = Field(..., examples=["Travel"])


class TransactionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    user_id: str
    description: str
    amount: float
    currency: str = "USD"
    txn_date: date
    merchant: str | None = None
    predicted_category: CategoryLiteral | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    category_source: SourceLiteral
    created_at: datetime


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    detail: str
