FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app
COPY . .

# Создаем виртуальное окружение и устанавливаем зависимости
RUN uv venv && uv sync --no-cache

# Делаем entrypoint.sh исполняемым
RUN chmod +x entrypoint.sh

# Запускаем приложение через entrypoint
ENTRYPOINT ["./entrypoint.sh"]
