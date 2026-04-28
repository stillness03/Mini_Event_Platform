FROM python:3.12-slim as builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY services/payment-service/requirements.txt .
COPY shared /shared

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
RUN pip install --no-cache-dir --prefix=/install /shared


FROM python:3.12-slim

WORKDIR /services/payment-service

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*


COPY --from=builder /install /usr/local

COPY services/payment-service/ .
COPY shared /shared

COPY services/payment-service/deploy/entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

RUN useradd -m payuser && \
    chown -R payuser /services/payment-service /shared

USER payuser

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/services/payment-service:/shared

EXPOSE 8003

ENTRYPOINT ["entrypoint.sh"]