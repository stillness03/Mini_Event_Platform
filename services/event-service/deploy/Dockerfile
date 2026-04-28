FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY services/event-service/requirements.txt .
COPY shared /shared

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
RUN pip install --no-cache-dir --prefix=/install /shared

FROM python:3.12-slim

WORKDIR /services/event-service

COPY --from=builder /install /usr/local

COPY services/event-service/ .
COPY shared /shared

RUN useradd -m appuser && chown -R appuser /services/event-service /shared
USER appuser

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/services/event-service:/shared

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]