# ==============================================================================
# 🌌 STAGE 1: THE INFRASTRUCTURE COMPILATION CONTAINER (BUILDENV)
# ==============================================================================
FROM python:3.12-slim-noble AS builder

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

# Compile your third-party wheels natively directly into a local wheel cache directory
RUN python -m pip install --upgrade pip && \
    python -m pip wheel --no-cache-dir --wheel-dir /build/wheels -r requirements.txt

# ==============================================================================
# 🌌 STAGE 2: THE HARDENED ZERO-TRUST RUNTIME EDGE CONTAINER
# ==============================================================================
FROM python:3.12-slim-noble

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Provision strictly the runtime Linux TCG software stack components, omitting compiler paths
RUN apt-get update && apt-get install -y --no-install-recommends \
    libtss2-dev \
    && rm -rf /var/lib/apt/lists/*

# Extract only the fully compiled production binary wheels from the builder image layers
COPY --from=builder /build/wheels /app/wheels
RUN python -m pip install --no-cache-dir /app/wheels/* && \
    rm -rf /app/wheels

# Ingest your multi-layer obfuscated logic modules and text vault assets cleanly into the image
COPY . /app/

# Establish an unprivileged runtime user account to block root escalation vectors inside the container
RUN useradd -u 10001 -m vivic_operator && \
    chown -R vivic_operator:vivic_operator /app
USER vivic_operator

# Execute the repository configuration validation engine at active container launch
ENTRYPOINT ["python", "validate_config.py"]
