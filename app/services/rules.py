from __future__ import annotations

from dataclasses import dataclass

from app.schemas.transaction import CATEGORIES, CategoryLiteral


@dataclass
class RuleResult:
    merchant: str | None
    category: CategoryLiteral
    confidence: float
    reason: str


_KEYWORD_RULES: dict[CategoryLiteral, list[str]] = {
    "Transportation": ["uber", "lyft", "taxi", "metro"],
    "Dining": ["doordash", "ubereats", "restaurant", "cafe", "starbucks"],
    "Subscriptions": ["netflix", "spotify", "apple.com/bill"],
    "Income": ["payroll", "salary", "stripe payout"],
    "Rent": ["rent"],
    "Utilities": ["electric", "water", "gas bill", "internet"],
    "Travel": ["airbnb", "hotel", "flight", "delta", "united"],
}

_GROCERY_KEYWORDS = ["whole foods", "walmart", "target", "trader joe"]


def _extract_merchant(description: str) -> str | None:
    normalized = description.strip()
    if not normalized:
        return None
    head = normalized.split(" ")[0].strip("-:,. ")
    return head.title() if head else None


def categorize_by_rules(description: str, amount: float) -> RuleResult:
    normalized = description.lower()

    for category, keywords in _KEYWORD_RULES.items():
        for keyword in keywords:
            if keyword in normalized:
                confidence = 0.92 if len(keyword) > 4 else 0.85
                return RuleResult(
                    merchant=_extract_merchant(description),
                    category=category,
                    confidence=confidence,
                    reason=f"Matched keyword '{keyword}' for {category}.",
                )

    for keyword in _GROCERY_KEYWORDS:
        if keyword in normalized:
            if keyword == "target":
                category: CategoryLiteral = "Shopping"
                reason = "Target purchases are often mixed goods; defaulting to Shopping."
                confidence = 0.74
            else:
                category = "Groceries"
                reason = f"Matched grocery merchant '{keyword}'."
                confidence = 0.82
            return RuleResult(
                merchant=_extract_merchant(description),
                category=category,
                confidence=confidence,
                reason=reason,
            )

    fallback_category: CategoryLiteral = "Other"
    if fallback_category not in CATEGORIES:
        raise ValueError("Fallback category is not configured.")

    amount_hint = "income-like" if amount < 0 else "expense-like"
    return RuleResult(
        merchant=_extract_merchant(description),
        category=fallback_category,
        confidence=0.45,
        reason=f"No rule match found; defaulted to Other ({amount_hint} transaction).",
    )
