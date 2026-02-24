import logging
import httpx
from fastapi import Depends, APIRouter, Request, Response
from app.core.config import Settings, get_settings
import pybreaker

router = APIRouter()
logger = logging.getLogger("gateway")

PROXY_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]

breaker = {
    "users" : pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30),
    "events" : pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30),
    "subscriptions" : pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30)
}

@breaker
async def _call(client, method, url, headers, content, params):
    return await client.request(
        method=method, url=url,
        headers=headers, content=content, params=params
    )

def _build_headers(request: Request) -> dict: 
    skip = {"host", "content-length", "transfer-encoding"} 
    headers = { k: v for k, v in request.headers.items() if k.lower() not in skip } 
    headers["X-Correlation-ID"] = getattr( 
        request.state, 
        "correlation_id", 
        "" 
    ) 
    return headers

async def forward_request(request: Request, target_base_url: str, settings: Settings, service_name: str):
    b = breaker[service_name]
    async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
        try:
            response = await b.call_async(
                _call,
                client,
                method=request.method,
                url=f"{target_base_url}{request.url.path}",
                headers=_build_headers(request),
                content=await request.body(),
                params=request.query_params,
            )
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers={k: v for k, v in response.headers.items() if k.lower() in ALLOWED_HEADERS},
            )
        except httpx.RequestError as exc:
            logger.error(f"Proxy error -> {target_base_url} : {exc}")
            return Response(
                content=b'{"detail":"Service unavailable"}',
                status_code=503,
                media_type="application/json",
            )
        
        except pybreaker.CircuitBreakerError:
            logger.warning(f"Circuit open for {target_base_url}")
            return Response(
                    content=b'{"detail":"Service temporarily unavailable"}',
                    status_code=503,
                    media_type="application/json",
                )


@router.api_route("/users/{path:path}", methods=PROXY_METHODS)
async def users_proxy(path: str, request: Request, settings: Settings = Depends(get_settings)):
    return await forward_request(request, settings.USER_SERVICE_URL, settings, "users")


@router.api_route("/events/{path:path}", methods=PROXY_METHODS)
async def events_proxy(path: str, request: Request, settings: Settings = Depends(get_settings)):
    return await forward_request(request, settings.EVENT_SERVICE_URL, settings, "events")


@router.api_route("/subscriptions/{path:path}", methods=PROXY_METHODS)
async def subs_proxy(path: str, request: Request, settings: Settings = Depends(get_settings)):
    return await forward_request(request, settings.SUB_SERVICE_URL, settings, "subscriptions")