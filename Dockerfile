# syntax=docker/dockerfile:1
ARG BASE_IMAGE=python:3.12-slim

# === STAGE 1: BUILDER ===
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

RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip setuptools wheel && \
    python -m pip wheel \
      --wheel-dir /build/wheels \
      --index-url https://pypi.org \
      --extra-index-url https://pytorch.org \
      -r requirements-runtime.txt .

# === STAGE 2: RUNTIME ===
FROM ${BASE_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libtss2-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Inherit pre-compiled dependencies from builder stage
COPY --from=builder /build/wheels /app/wheels
COPY requirements-runtime.txt /app/
COPY . /app/

# Inject native signal-forwarding entrypoint configuration block safely inside the active WORKDIR
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

RUN useradd -u 10001 -m -s /sbin/nologin vivic_operator && \
    python -m pip install \
      --no-cache-dir \
      --no-compile \
      --no-index \
      --find-links=/app/wheels \
      -r /app/requirements-runtime.txt \
      the-frequency-project && \
    rm -rf /app/wheels /root/.cache/pip

RUN find /usr/local/lib/python3.12/site-packages -type d -name '__pycache__' -prune -exec rm -rf {} + && \
    find /usr/local/lib/python3.12/site-packages -type f -name '*.py[co]' -delete

RUN mkdir -p /app/scratch && \
    chown -R root:root /app && \
    chown -R vivic_operator:vivic_operator /app/scratch && \
    chmod -R 0555 /app && \
    chmod -R 0700 /app/scratch

EXPOSE 8000
USER vivic_operator

ENTRYPOINT ["/app/entrypoint.sh"]
