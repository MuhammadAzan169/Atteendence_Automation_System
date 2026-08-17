# syntax=docker/dockerfile:1

# ==========================================================
# Attendance Automation System — backend API
# Two stages: dependencies are built in a throwaway image and
# only the finished virtualenv is copied into the runtime one,
# so pip and its build artefacts never ship.
# ==========================================================

# ---------- stage 1: build the virtualenv -----------------
FROM python:3.11-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# Every dependency (Pillow, psycopg2-binary, reportlab) publishes manylinux
# wheels with its native libraries bundled, so no compiler or -dev package
# is needed here.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

# ---------- stage 2: runtime ------------------------------
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app

# Run as a normal user; nothing in the app needs root.
RUN useradd --create-home --uid 10001 appuser

COPY --chown=appuser:appuser . .

# SQLite lives here when DATABASE_URL is unset. On a host with a disposable
# filesystem (Render free) mount a volume over it or use Postgres instead.
RUN mkdir -p /app/database && chown appuser:appuser /app/database
VOLUME ["/app/database"]

USER appuser

EXPOSE 5000

# Uses the app's own health endpoint. Written in Python so the image does not
# need curl or wget installed.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD ["python", "-c", "import os,urllib.request;urllib.request.urlopen('http://127.0.0.1:'+os.environ.get('PORT','5000')+'/api/health',timeout=4)"]

# exec form + `exec` so gunicorn becomes PID 1 and receives SIGTERM directly;
# without it Docker/Render would wait out the full grace period on every stop.
# The shell wrapper is what expands $PORT, which Render injects at runtime.
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-5000} --workers ${WEB_CONCURRENCY:-2} --timeout 120 --access-logfile - --error-logfile - wsgi:app"]
