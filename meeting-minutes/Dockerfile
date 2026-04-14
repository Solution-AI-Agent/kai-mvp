# ============================================================
# Stage 1: Build React (Vite) frontend
# ============================================================
FROM node:20-alpine AS web-builder
WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ============================================================
# Stage 2: Runtime (Python + nginx, single image)
# ============================================================
FROM python:3.11-slim AS runtime
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        nginx \
    && rm -rf /var/lib/apt/lists/*

# openai-whisper's setup.py imports pkg_resources (removed in setuptools 81)
RUN pip install --upgrade pip && pip install "setuptools<81" wheel

# CPU-only torch — skips ~5GB of CUDA wheels (local demo doesn't need GPU)
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

COPY backend/requirements.txt ./
RUN pip install --no-build-isolation -r requirements.txt

COPY backend/ ./backend/

# Built frontend assets served by nginx
COPY --from=web-builder /app/dist /var/www/html

COPY nginx.conf /etc/nginx/sites-available/default
COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 9010 9011

CMD ["/start.sh"]
