import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from src.core.logging_config import get_logger

logger = get_logger()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id

        t0 = time.time()
        try:
            response = await call_next(request)
        except Exception:
            latency_ms = int((time.time() - t0) * 1000)
            logger.exception(
                "request_failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "latency_ms": latency_ms,
                },
            )
            raise

        latency_ms = int((time.time() - t0) * 1000)
        response.headers["x-request-id"] = request_id

        logger.info(
            "request_ok",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "latency_ms": latency_ms,
                "client": request.client.host if request.client else None,
            },
        )
        return response