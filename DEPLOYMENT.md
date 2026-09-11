# 🚀 The Frequency Project: Production Deployment Runbook

This document details the configuration profiles, security policies, and orchestration steps required to deploy the high-assurance ecological telemetry ingestion pipeline in a production environment.

## 🏗️ 1. Multi-Stage Container Architecture

The system is deployed using a hardened, multi-stage Docker configuration that isolates build-time compilers from the raw runtime environment. 

### 🛡️ Production Security Baselines
- **Rootless Execution:** The container runs under a non-privileged system user profile (`UID 10001`), preventing container-breakout escalation hazards.
- **Read-Only Filesystem:** The container root file tree is mounted as completely read-only (`read_only: true`). Writable state requirements are restricted strictly to memory-backed volatile partitions (`/tmp`).
- **Resource Constraints:** Heavy deep learning tensor allocations are isolated and constrained to prevent out-of-memory worker crashes or thread scheduling thrashing on shared host hardware.
- **Network Isolation:** The observability matrix is isolated and exposed on port 8000/tcp via lightweight HTTP raw sockets, bypassing heavy application framework overhead.

## 🎛️ 2. Environmental Configuration Profiles

The application state parameters are driven cleanly via environmental variables. Avoid hardcoding variables within secondary scripts.

| Environment Variable | Production Setting | Purpose |
|----------------------|--------------------|---------|
| `OMP_NUM_THREADS`     | `1`                | Eliminates multi-threaded scheduling collisions in OpenMP |
| `MKL_NUM_THREADS`     | `1`                | Constrains Intel MKL math operations to single-thread |
| `OPENBLAS_NUM_THREADS`| `1`                | Limits OpenBLAS background worker pools |
| `VECLIB_MAXIMUM_THREADS` | `1`             | Restricts Apple VecLib thread exhaustion cascades |
| `NUMEXPR_NUM_THREADS` | `1`                | Hardens acceleration math against thread leaks |
| `TPM2TOOLS_TCTI`     | `mssim:port=2321`  | Directs transport protocols to the emulation proxy |

## 🔒 3. Local Hardware Security Module (TPM 2.0) Setup

Before spinning up the orchestrator container on edge equipment, instantiate an isolated software socket using `swtpm` to validate the cryptographic exception taxonomies and unseal keys natively.

```bash
# 1. Provision a dedicated state directory tracking variables securely
mkdir -p /tmp/mytpm

# 2. Launch the swtpm socket background daemon proxy
swtpm socket --tpmstate dir=/tmp/mytpm \
             --tpm2 \
             --server port=2321 \
             --ctrl port=2322 \
             --flags startup-clear &
```

## 🚀 4. Execution & Orchestration Controls

To deploy the production-ready application stack smoothly, run the unified launch command from your host environment terminal layer:

```bash
# Build the production container utilizing multi-stage cache layers
docker build -t local/the-frequency-project:latest .

# Instantiate the container instance with strict runtime limits and read-only mounts
docker run -d \
  --name operational-ingestion-engine \
  -p 8000:8000 \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  --user 10001:10001 \
  -e OMP_NUM_THREADS=1 \
  -e MKL_NUM_THREADS=1 \
  -e OPENBLAS_NUM_THREADS=1 \
  -e VECLIB_MAXIMUM_THREADS=1 \
  -e NUMEXPR_NUM_THREADS=1 \
  -e TPM2TOOLS_TCTI="mssim:port=2321" \
  --network host \
  local/the-frequency-project:latest

```

## 🛑 5. Graceful Teardown and Signal Interception

The orchestration layer features native POSIX signal hooks capturing container termination requests cleanly:
- When a `docker stop` or `SIGTERM` (Signal 15) code hits the process context, the runtime intercepts the trap, flips `session.is_active = False`, and calls `daemon.stop()` cleanly.
- This guarantees background asynchronous serial ingestion frames drop out sequentially, avoiding byte-level array fragmentation on your active hardware communication lines.

```

## 📊 6. Cloud Observability & Orchestrator Probes

The embedded HTTP metrics server on port `8000` satisfies cloud-native infrastructure automation specifications out of the box:

### 🐋 Docker / Kubernetes Orchestrator Probes
The `/health` endpoint responds dynamically based on internal calibration states to drive automation pipelines:
- **`200 OK`**: System is calibrated or running operational loops (`{"status": "HEALTHY"}`).
- **`503 Service Unavailable`**: Queues are warming up or calibrating (`{"status": "INITIALIZING"}`).

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
```

### 📈 Prometheus Target Scraping Matrix
The `/metrics` endpoint exports plain-text telemetry arrays mapping to standard Prometheus exposition formats (v0.0.4).

**Exported Metrics Reference:**
- `vivic_total_packets_parsed` (Counter): Cumulative sum of processed telemetry packets.
- `vivic_anomalies_detected` (Counter): Cumulative sum of flagged 3-Sigma anomalies.
- `vivic_session_status{status="active"}` (Gauge): Active cycle loop state (1=Active, 0=Stopped).
- `vivic_session_status{status="calibrated"}` (Gauge): Ambient noise baseline status (1=Calibrated, 0=Uncalibrated).
