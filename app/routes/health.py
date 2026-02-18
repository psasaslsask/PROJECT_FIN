from fastapi import APIRouter, Response, status

router = APIRouter(tags=["health"])


@router.get("/", summary="Service root")
def service_root() -> dict[str, str]:
    return {"status": "ok", "docs": "/docs"}


@router.get("/health", summary="Health check")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    return Response(status_code=status.HTTP_204_NO_CONTENT)
