FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Build deps for Pillow (qrcode) and psycopg2 wheels.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libjpeg62-turbo zlib1g \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p database

EXPOSE 5000

# Render injects $PORT; default to 5000 elsewhere.
CMD gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120 wsgi:app
