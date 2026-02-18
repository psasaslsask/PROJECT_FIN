from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import configure_logging
from app.routes.categorize import router as categorize_router
from app.routes.health import router as health_router
from app.routes.transactions import router as transactions_router

configure_logging()

app = FastAPI(title=settings.app_name, version=settings.app_version)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    message = "; ".join(
        [f"{'/'.join(map(str, err['loc']))}: {err['msg']}" for err in exc.errors()]
    )
    return JSONResponse(status_code=400, content={"detail": message})


app.include_router(health_router)
app.include_router(categorize_router)
app.include_router(transactions_router)
