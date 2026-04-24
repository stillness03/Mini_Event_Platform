import httpx

def create_http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=httpx.Timeout(
            connect=2.0,
            read=5.0,
            write=5.0,
            pool=2.0
        ),
        limits=httpx.Limits(
            max_connections=100,
            max_keepalive_connections=20
        ),

        follow_redirects=False,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "PaymentService/1.0"
        }
    )

