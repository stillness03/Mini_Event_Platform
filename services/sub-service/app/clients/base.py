import httpx


def create_http_client() -> httpx.AsyncClient:
    timeout = httpx.Timeout(
        timeout=5.0,
        connect=2.0,
        read=5.0,
        write=5.0,
    )

    limits = httpx.Limits(
        max_connections=100,
        max_keepalive_connections=20
    )

    return httpx.AsyncClient(
        timeout=timeout,
        limits=limits,
        follow_redirects=True,
        headers={
            "Content-Type": "application/json",
        },
    )