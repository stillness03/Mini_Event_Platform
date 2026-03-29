import logging
import asyncio
import httpx

from fastapi import Depends, APIRouter, Request, Response
from app.core.config import Settings, get_settings
from aiobreaker import CircuitBreaker, CircuitBreakerError

router = APIRouter()
logger = logging.getLogger("gateway")
settings = get_settings()

PROXY_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]
ALLOWED_HEADERS = {"content-type", "content-length"}

#Circuit Breakers
breaker = {
    "users": CircuitBreaker(fail_max=5, timeout_duration=30),
    "events": CircuitBreaker(fail_max=5, timeout_duration=30),
    "subscriptions": CircuitBreaker(fail_max=5, timeout_duration=30),
}

# Utils
def _build_headers(request: Request) -> dict:
    skip = {"host", "content-length", "transfer-encoding"}

    headers = {
        k: v
        for k, v in request.headers.items()
        if k.lower() not in skip
    }

    # Retrieving the user ID from the middleware
    user_data = getattr(request.state, "user", None)

    if user_data:
        user_id = user_data.get("sub") or user_data.get("user_id")
        if not user_id:
            logger.error(f"Invalid user_data: {user_data}")
            raise ValueError("Unauthorized: user missing")

        headers["X-User-Id"] = str(user_id)
        headers["X-User-Role"] = str(user_data.get("role", "user"))

    headers["X-Correlation-ID"] = getattr(request.state, "correlation_id", "")
    logger.info(f"Outgoing headers: {headers}")
    return headers

async def _call(client, method, url, headers, content, params):
    return await client.request(
        method=method,
        url=url,
        headers=headers,
        content=content,
        params=params
    )


async def _call_with_retry(client, request, target_url, settings: Settings):
    """Retry + backoff"""
    last_exc = None

    for attempt in range(1, settings.MAX_RETRIES + 1):
        try:
            headers = _build_headers(request)

            return await _call(
                client,
                method=request.method,
                url=target_url,
                headers=headers,
                content=await request.body(),
                params=request.query_params,
            )

        except ValueError:
            # if user none = error 401
            raise

        except httpx.RequestError as exc:
            last_exc = exc
            logger.warning(f"Retry {attempt}/{settings.MAX_RETRIES} failed: {exc}")

            if attempt < settings.MAX_RETRIES:
                await asyncio.sleep(settings.RETRY_BACKOFF * attempt)

    raise last_exc



# Core proxy logic
async def forward_request(
    request: Request,
    target_base_url: str,
    settings: Settings,
    service_name: str,
    path: str
):
    b = breaker[service_name]

    target_url = f"{str(target_base_url).rstrip('/')}/{path.lstrip('/')}"

    async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
        try:
            logger.info(f"{request.method} -> {target_url}")

            # Circuit Breaker + Retry
            response = await b.call_async(
                _call_with_retry,
                client,
                request,
                target_url,
                settings
            )

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers={
                    k: v
                    for k, v in response.headers.items()
                    if k.lower() in ALLOWED_HEADERS
                },
            )

        except ValueError:
            return Response(
                content=b'{"detail":"Unauthorized"}',
                status_code=401,
                media_type="application/json",
            )

        # Circuit OPEN
        except CircuitBreakerError:
            logger.error(f"Circuit OPEN for {service_name}")

            return Response(
                content=b'{"detail":"Service temporarily unavailable"}',
                status_code=503,
                media_type="application/json",
            )

        # Network / timeout errors
        except httpx.RequestError as exc:
            logger.error(f"Proxy error -> {target_url} : {exc}")

            return Response(
                content=b'{"detail":"Service unavailable"}',
                status_code=503,
                media_type="application/json",
            )

        # Unexpected errors
        except Exception as exc:
            logger.exception(f"Unexpected error: {exc}")

            return Response(
                content=b'{"detail":"Internal gateway error"}',
                status_code=500,
                media_type="application/json",
            )



# Routes
@router.api_route("/events", methods=PROXY_METHODS)
@router.api_route("/events/{path:path}", methods=PROXY_METHODS)
async def events_proxy(
    path: str = "",
    request: Request = None,
    settings: Settings = Depends(get_settings)
):
    full_path = f"events/{path}".rstrip("/")  # ← "events" або "events/123"
    return await forward_request(
        request, settings.EVENT_SERVICE_URL, settings, "events", full_path
    )


@router.api_route("/users", methods=PROXY_METHODS)
@router.api_route("/users/{path:path}", methods=PROXY_METHODS)
async def users_proxy(
    path: str = "",
    request: Request = None,
    settings: Settings = Depends(get_settings)
):
    full_path = f"users/{path}".rstrip("/")
    return await forward_request(
        request, settings.USER_SERVICE_URL, settings, "users", full_path
    )


@router.api_route("/subscriptions", methods=PROXY_METHODS)
@router.api_route("/subscriptions/{path:path}", methods=PROXY_METHODS)
async def subs_proxy(
    path: str = "",
    request: Request = None,
    settings: Settings = Depends(get_settings)
):
    full_path = f"subscriptions/{path}".rstrip("/")
    return await forward_request(
        request, settings.SUB_SERVICE_URL, settings, "subscriptions", full_path
    )