FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y libpq-dev gcc netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
