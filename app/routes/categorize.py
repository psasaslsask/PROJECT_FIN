from fastapi import APIRouter

from app.schemas.transaction import CategorizeRequest, CategorizeResponse
from app.services.ai_client import categorize_transaction

router = APIRouter(prefix="/v1", tags=["categorization"])


@router.post(
    "/categorize",
    response_model=CategorizeResponse,
    response_model_exclude_none=False,
    summary="Categorize a transaction",
)
def categorize(payload: CategorizeRequest) -> CategorizeResponse:
    result = categorize_transaction(
        description=payload.description,
        amount=payload.amount,
        currency=payload.currency,
        txn_date=payload.txn_date.isoformat(),
    )
    return result
