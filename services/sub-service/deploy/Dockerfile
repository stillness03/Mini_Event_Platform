FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY services/sub-service/requirements.txt .
COPY shared /shared

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
RUN pip install --no-cache-dir --prefix=/install /shared

FROM python:3.12-slim

WORKDIR /services/sub-service

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

COPY services/sub-service/ .
COPY shared /shared

COPY services/sub-service/deploy/entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

RUN useradd -m subuser && \
    chown -R subuser /services/sub-service /shared

USER subuser

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


ENV PYTHONPATH=/services/sub-service:/shared

EXPOSE 8002

ENTRYPOINT ["entrypoint.sh"]