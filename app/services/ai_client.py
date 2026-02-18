from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from app.core.config import settings
from app.schemas.transaction import CATEGORIES, CategorizeResponse
from app.services.rules import categorize_by_rules

logger = logging.getLogger(__name__)


def _build_prompt(description: str, amount: float, currency: str, txn_date: str) -> str:
    return (
        "Categorize this transaction and return strict JSON with keys: "
        "merchant, category, confidence, reason. "
        f"Allowed categories: {', '.join(CATEGORIES)}. "
        f"Transaction: description={description!r}, amount={amount}, currency={currency}, txn_date={txn_date}."
    )


def _mock_ai(description: str, amount: float, currency: str, txn_date: str) -> CategorizeResponse:
    _ = (currency, txn_date)
    rule_result = categorize_by_rules(description, amount)
    return CategorizeResponse(
        merchant=rule_result.merchant,
        category=rule_result.category,
        confidence=min(0.99, max(0.0, round(rule_result.confidence, 2))),
        reason=f"Mock AI: {rule_result.reason}",
    )


def _parse_and_validate(payload: dict[str, Any]) -> CategorizeResponse:
    model = CategorizeResponse.model_validate(payload)
    if model.category not in CATEGORIES:
        raise ValueError("Invalid category from AI response")
    return model


def categorize_transaction(description: str, amount: float, currency: str, txn_date: str) -> CategorizeResponse:
    if not settings.openai_api_key:
        return _mock_ai(description, amount, currency, txn_date)

    prompt = _build_prompt(description, amount, currency, txn_date)
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": settings.openai_model,
        "messages": [
            {
                "role": "system",
                "content": "You are a transaction categorizer. Reply with JSON only.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
    }

    try:
        with httpx.Client(timeout=settings.request_timeout_seconds) as client:
            response = client.post(f"{settings.openai_base_url}/chat/completions", headers=headers, json=body)
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return _parse_and_validate(parsed)
    except Exception as exc:  # fallback is intentional for resilience
        logger.warning("AI categorization failed, falling back to rules: %s", exc)
        rule_result = categorize_by_rules(description, amount)
        return CategorizeResponse(
            merchant=rule_result.merchant,
            category=rule_result.category,
            confidence=round(rule_result.confidence, 2),
            reason=f"Rule fallback: {rule_result.reason}",
        )
