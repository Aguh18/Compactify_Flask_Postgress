# Use Python 3.10 slim image as base (stable and compatible)
FROM python:3.10-slim

# Set working directory in container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_DEFAULT_TIMEOUT=300

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libc6-dev \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip to latest version
RUN pip install --upgrade pip

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies with timeout and retries
RUN pip install --no-cache-dir \
    --timeout 300 \
    --retries 5 \
    -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p app/static/uploads \
    && mkdir -p app/static/CompressImg \
    && mkdir -p app/static/CompressPdf \
    && mkdir -p app/static/docToPdf \
    && mkdir -p app/static/imagetopdf \
    && mkdir -p app/static/imgtogray \
    && mkdir -p app/static/removeBackground \
    && mkdir -p app/static/zip \
    && mkdir -p app/static/CompressAudio

# Set permissions for upload directories
RUN chmod 755 app/static/uploads \
    && chmod 755 app/static/CompressImg \
    && chmod 755 app/static/CompressPdf \
    && chmod 755 app/static/docToPdf \
    && chmod 755 app/static/imagetopdf \
    && chmod 755 app/static/imgtogray \
    && chmod 755 app/static/removeBackground \
    && chmod 755 app/static/zip \
    && chmod 755 app/static/CompressAudio

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=server.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Run the application
CMD ["python", "server.py"]
