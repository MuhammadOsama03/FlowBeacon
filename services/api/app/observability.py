import json
import logging
import re
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


logger = logging.getLogger("flowbeacon.requests")
REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{8,64}$")


class RequestObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        supplied = request.headers.get("x-request-id", "")
        request_id = supplied if REQUEST_ID.fullmatch(supplied) else uuid.uuid4().hex
        started = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        logger.info(json.dumps({"event": "http_request", "request_id": request_id,
            "method": request.method, "path": request.url.path,
            "status": response.status_code, "duration_ms": elapsed_ms}, separators=(",", ":")))
        return response
