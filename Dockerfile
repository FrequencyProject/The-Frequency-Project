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

# Install bare-metal C-compiler tools, system development headers, and pkg-config
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    libtss2-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy the hardened python dependency and supply chain configuration manifests
COPY requirements.txt pyproject.toml ./

# HARDENING REMEDIATION: Inject BuildKit persistent cache mounts straight into the compiler paths.
# This prevents pip from re-downloading massive multi-gigabyte wheels if requirements are unchanged.
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip setuptools && \
    python -m pip wheel --wheel-dir /build/wheels -r requirements.txt

# ==============================================================================
# 🌌 STAGE 2: THE HARDENED ZERO-TRUST RUNTIME EDGE CONTAINER
# ==============================================================================
ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Provision strictly the runtime Linux TCG software stack components, omitting compiler paths
RUN apt-get update && apt-get install -y --no-install-recommends \
    libtss2-dev \
    && rm -rf /var/lib/apt/lists/*

# Extract the fully compiled production binary wheels from the builder image layers
COPY --from=builder /build/wheels /app/wheels

# Establish the unprivileged system user account before copying tracking modules
RUN useradd -u 10001 -m -s /sbin/nologin vivic_operator

# Ingest your multi-layer logic modules cleanly into the workspace image
COPY . /app/

# HARDENING REMEDIATION: Layer Synchronization for Flat-Layout Packages.
# Executes installation *after* source ingestion, ensuring the local package module layout 
# is cleanly compiled and mounted directly onto Python's system path alongside dependencies.
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --no-index --find-links=/app/wheels /app/wheels/* . && \
    rm -rf /app/wheels

# HARDENING REMEDIATION: Principle of Least Privilege / Immutable Source Code Invariant.
# 1. Source files are strictly owned by root and kept READ-ONLY (0555) so the application process
#    can never overwrite its own running Python code modules during a remote attack exploit.
# 2. Provision an isolated, non-executable storage workspace for runtime ephemeral data logs.
RUN mkdir -p /app/scratch && \
    chown -R root:root /app && \
    chown -R vivic_operator:vivic_operator /app/scratch && \
    chmod -R 0555 /app && \
    chmod -R 0700 /app/scratch

# Bind execution strictly to the unprivileged account context
USER vivic_operator

# Execute the repository configuration validation engine at active container launch
ENTRYPOINT ["python", "validate_config.py"]
