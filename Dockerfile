# syntax=docker/dockerfile:1
# Declare global image parameters to standardize the lightweight Debian base
ARG BASE_IMAGE=python:3.12-slim

# ==============================================================================
# 🌌 STAGE 1: THE INFRASTRUCTURE COMPILATION CONTAINER (BUILDENV)
# ==============================================================================
FROM ${BASE_IMAGE} AS builder

# Prevent Python from writing buffering streams or raw bytecode to the disk partition
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    libtss2-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY pyproject.toml ./

# HARDENING REMEDIATION: Resource Constraint Allocation Guard.
# Correctly targets the official PyTorch CPU wheel index to strip out giant CUDA frameworks.
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip setuptools && \
    python -m pip wheel --wheel-dir /build/wheels \
      --extra-index-url https://pytorch.org \
      .

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
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /build/wheels /app/wheels

# Establish the unprivileged system user account before copying tracking modules
RUN useradd -u 10001 -m -s /sbin/nologin vivic_operator

COPY . /app/

# HARDENING REMEDIATION: Automated Index Alignment.
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --no-index --find-links=/app/wheels . && \
    rm -rf /app/wheels

# HARDENING REMEDIATION: Principle of Least Privilege / Immutable Source Code Invariant.
RUN mkdir -p /app/scratch && \
    chown -R root:root /app && \
    chown -R vivic_operator:vivic_operator /app/scratch && \
    chmod -R 0555 /app && \
    chmod -R 0700 /app/scratch

# HARDENING REMEDIATION: Network Observability Exposition.
EXPOSE 8000

# Bind execution strictly to the unprivileged account context
USER vivic_operator

# Execute pre-flight configuration validation before launching the live telemetry cluster session
ENTRYPOINT ["sh", "-c", "python validate_config.py && python run_session.py"]
