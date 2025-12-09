# Build stage
FROM ubuntu:24.04 as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

# Install Python 3.11 and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-venv \
    python3-pip \
    gcc \
    g++ \
    libc6-dev \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python3.11 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN . /opt/venv/bin/activate && pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM ubuntu:24.04

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=server.py \
    FLASK_ENV=production \
    PYTHONPATH=/app \
    OPENCV_LOG_LEVEL=ERROR \
    DEBIAN_FRONTEND=noninteractive

# Install Python 3.11 and runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-venv \
    libpq5 \
    curl \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment dari builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p app/static/uploads \
    app/static/CompressImg \
    app/static/CompressPdf \
    app/static/docToPdf \
    app/static/imagetopdf \
    app/static/imgtogray \
    app/static/removeBackground \
    app/static/zip \
    app/static/CompressAudio \
    /tmp/gunicorn_tmp && \
    chmod -R 755 app/static/ && \
    chmod 777 /tmp/gunicorn_tmp

EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Run migration and start app
CMD ["/bin/bash", "-c", "source /opt/venv/bin/activate && flask db upgrade && gunicorn --bind 0.0.0.0:5000 --workers 4 --worker-class sync --timeout 120 --max-requests 1000 --max-requests-jitter 100 --access-logfile - --error-logfile - server:app"]
