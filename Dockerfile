# syntax=docker/dockerfile:1
ARG BASE_IMAGE=python:3.12-slim

FROM ${BASE_IMAGE} AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    libtss2-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY pyproject.toml README.md requirements-runtime.txt ./
COPY . .

# CRITICAL FIX: Explicitly target the lightweight CPU wheel index to strip 4+ GB of CUDA components
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip setuptools wheel && \
    python -m pip wheel \
      --wheel-dir /build/wheels \
      --index-url https://pytorch.org \
      --extra-index-url https://pypi.org \
      -r requirements-runtime.txt .

ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libtss2-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /build/wheels /app/wheels
COPY requirements-runtime.txt /app/
COPY . /app/

# CRITICAL FIX: Enforce --no-compile and aggressively prune bytecode directories to prevent disk spikes
RUN useradd -u 10001 -m -s /sbin/nologin vivic_operator && \
    python -m pip install \
      --no-cache-dir \
      --no-compile \
      --no-index \
      --find-links=/app/wheels \
      -r /app/requirements-runtime.txt \
      the-frequency-project && \
    rm -rf /app/wheels /root/.cache/pip

# Clean out any leftover bytecode items to protect the final overlay export
RUN find /usr/local/lib/python3.12/site-packages -type d -name '__pycache__' -prune -exec rm -rf {} + && \
    find /usr/local/lib/python3.12/site-packages -type f -name '*.py[co]' -delete

RUN mkdir -p /app/scratch && \
    chown -R root:root /app && \
    chown -R vivic_operator:vivic_operator /app/scratch && \
    chmod -R 0555 /app && \
    chmod -R 0700 /app/scratch

# Synchronized production application port
EXPOSE 8000
USER vivic_operator

ENTRYPOINT ["sh", "-c", "python validate_config.py && python run_session.py"]
