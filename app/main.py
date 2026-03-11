import uuid

import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import settings
from app.logging import configure_logging
from app.routers import image_lead, inquiry, sales_eval, slide, suggestion, voice_lead
from app.request_context import request_id_var
from app.schemas.common import ErrorResponse

configure_logging(settings.log_level)
logger = structlog.get_logger(__name__)

app = FastAPI(title="Salesforce AI Service", version=settings.app_version)


@app.middleware("http")
async def attach_request_id(request: Request, call_next):
    request_id = request.headers.get("x-request-id", f"req_{uuid.uuid4()}")
    token = request_id_var.set(request_id)
    request.state.request_id = request_id
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("unhandled_exception", path=str(request.url.path))
        raise
    finally:
        request_id_var.reset(token)
    response.headers["x-request-id"] = request_id
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    body = ErrorResponse(
        error="http_error",
        detail=str(exc.detail),
        request_id=getattr(request.state, "request_id", None),
    )
    return JSONResponse(status_code=exc.status_code, content=body.model_dump())


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    body = ErrorResponse(
        error="validation_error",
        detail=str(exc),
        request_id=getattr(request.state, "request_id", None),
    )
    return JSONResponse(status_code=422, content=body.model_dump())


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("server_error", error=str(exc))
    body = ErrorResponse(
        error="server_error",
        detail="Internal server error",
        request_id=getattr(request.state, "request_id", None),
    )
    return JSONResponse(status_code=500, content=body.model_dump())

app.include_router(inquiry.router, prefix="/inquiry", tags=["inquiry"])
app.include_router(image_lead.router, prefix="/image-lead", tags=["image-lead"])
app.include_router(voice_lead.router, prefix="/voice-lead", tags=["voice-lead"])
app.include_router(sales_eval.router, prefix="/sales-eval", tags=["sales-eval"])
app.include_router(suggestion.router, prefix="/suggestion", tags=["suggestion"])
app.include_router(slide.router, prefix="/slide", tags=["slide"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": settings.app_version}
