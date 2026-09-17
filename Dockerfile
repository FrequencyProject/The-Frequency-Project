# syntax=docker/dockerfile:1
ARG BASE_IMAGE=python:3.12-slim

# ==============================================================================
# 🌌 STAGE 1: INFRASTRUCTURE COMPILATION (BUILDENV)
# ==============================================================================
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

COPY pyproject.toml requirements.txt ./
# Copy source files to allow builder stage to compile the project wheel completely
COPY . .

# Build wheels for requirements AND the local project into the wheels folder
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip setuptools wheel && \
    python -m pip wheel --wheel-dir /build/wheels \
      --extra-index-url https://pytorch.org \
      -r requirements.txt .

# ==============================================================================
# 🌌 STAGE 2: THE HARDENED ZERO-TRUST RUNTIME EDGE CONTAINER
# ==============================================================================
ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libtss2-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-compiled wheels from the builder
COPY --from=builder /build/wheels /app/wheels

RUN useradd -u 10001 -m -s /sbin/nologin vivic_operator

# Copy source repository contents
COPY . /app/

# HARDENING REMEDIATION: Automated Index Alignment (Fast, offline install of pre-compiled wheels)
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --no-index --find-links=/app/wheels -r requirements.txt the-frequency-project && \
    rm -rf /app/wheels

# HARDENING REMEDIATION: Principle of Least Privilege
RUN mkdir -p /app/scratch && \
    chown -R root:root /app && \
    chown -R vivic_operator:vivic_operator /app/scratch && \
    chmod -R 0555 /app && \
    chmod -R 0700 /app/scratch

EXPOSE 8000
USER vivic_operator

# Execute pre-flight configuration validation before launching the live telemetry cluster session
ENTRYPOINT ["sh", "-c", "python validate_config.py && python run_session.py"]
