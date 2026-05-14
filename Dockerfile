# ── Base image ────────────────────────────────────────────────────────────────
FROM python:3.11-slim

# ── Working directory ──────────────────────────────────────────────────────────
WORKDIR /app

# ── Install dependencies ───────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy server files ──────────────────────────────────────────────────────────
COPY server_prod.py .
COPY server.py .

# ── Railway injects PORT env variable automatically ────────────────────────────
ENV PORT=8000

# ── Start production server ────────────────────────────────────────────────────
CMD ["python", "server_prod.py"]
