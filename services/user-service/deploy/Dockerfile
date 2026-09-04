FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY services/user-service/requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Final Stage ---
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копіюємо встановлені залежності
COPY --from=builder /install /usr/local

# Копіюємо вихідний код
COPY services/user-service /app/services/user-service
COPY shared /app/shared

# Налаштовуємо скрипт запуску
COPY services/user-service/deploy/entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

# Налаштовуємо користувача безпеки
RUN useradd -m appuser && \
    chown -R appuser:appuser /app

USER appuser

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

EXPOSE 8001

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["uvicorn", "services.user_service.main:app", "--host", "0.0.0.0", "--port", "8001"]