# syntax=docker/dockerfile:1

# ---- Stage 1: builder -------------------------------------------------------
# Installs dependencies into a self-contained prefix so the final image
# doesn't carry pip's build cache or any toolchain.
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
# Install into /install so we can copy just the packages into the runtime stage.
RUN pip install --prefix=/install -r requirements.txt

# ---- Stage 2: runtime -------------------------------------------------------
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Bring over only the installed dependencies from the builder stage.
COPY --from=builder /install /usr/local

# Copy the application source.
COPY linkedin_agent/ ./linkedin_agent/
COPY .streamlit/ ./.streamlit/
COPY main.py app.py ./

# Run as a non-root user for safety.
RUN useradd --create-home --uid 1000 appuser
USER appuser

ENTRYPOINT ["python", "main.py"]
