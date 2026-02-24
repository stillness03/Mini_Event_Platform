import uuid
import logging
import time
from fastapi import Request

logger = logging.getLogger("gateway")

async def logging_middleware(request: Request, call_next):
    correlation_id = (
    request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    )
    request.state.correlation_id = correlation_id

    logger.info(f"[{correlation_id}] -> {request.method} {request.url}")

    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start

    logger.info(
        f"[{correlation_id}] ← {response.status_code} "
        f"completed in {duration:.3f}s"
    )
    
    response.headers["X-Correlation-ID"] = correlation_id
    return response