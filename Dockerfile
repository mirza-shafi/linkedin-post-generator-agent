# syntax=docker/dockerfile:1

FROM python:3.12-slim

# Keep Python output unbuffered and skip .pyc files for cleaner container logs.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install dependencies first to leverage Docker layer caching.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the application source.
COPY linkedin_agent/ ./linkedin_agent/
COPY main.py .

# Run as a non-root user for safety.
RUN useradd --create-home --uid 1000 appuser
USER appuser

ENTRYPOINT ["python", "main.py"]
