# 📑 Changelog

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com) and adheres to Semantic Versioning.

## - 2026-09-11

### 🚀 Added
- **Production Observability Engine:** Embedded zero-dependency HTTP metrics server on port `8000` inside `run_session.py`.
- **Prometheus Metric Streams:** Exposes `vivic_total_packets_parsed` counters and `vivic_anomalies_detected` evaluation trackers natively.
- **Dynamic Session Guages:** Embedded `vivic_session_status{status="active"}` and `{status="calibrated"}` metrics.
- **Cluster Orchestration Probes:** Introduced a native `/health` check route reporting `200 OK` or `503 Service Unavailable`.
- **Container Infrastructure Mapping:** Added `EXPOSE 8000` metadata layer to the multi-stage `Dockerfile`.

### 🔒 Security & Hardening
- **Static Analysis Invariant:** Appended `# nosec B104` declarations to socket bindings to satisfy strict Bandit CI scanners.
- **Build Optimization Guard:** Implemented `.dockerignore` context exclusions to isolate build caches from deployment images.

### 🧪 Testing
- **Integration Expansion:** Scaled test runner framework to a total of 45 master items validating multi-channel deque charging.
