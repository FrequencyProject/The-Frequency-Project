#!/usr/bin/env python3
"""High-Assurance Unit Test Suite for Embedded Orchestrator HTTP Server.

Validates text formatting and diagnostic responses over Prometheus and Health routes.
"""
import socket
import time
import pytest
from run_session import MetricsHttpExporter, UnifiedVivicSession


def test_metrics_http_server_responds_with_prometheus_format():
    """Asserts that the metrics endpoint binds cleanly and returns standard text counters."""
    session = UnifiedVivicSession(port="MOCK_TEST_PORT")
    exporter = MetricsHttpExporter(session=session, host="127.0.0.1", port=18000)
    exporter.start()

    # Allow background thread a clean time-slice window to bind socket parameters safely
    time.sleep(0.2)

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("127.0.0.1", 18000))
        sock.sendall(b"GET /metrics HTTP/1.1\r\nHost: localhost\r\n\r\n")
        response = sock.recv(4096).decode('utf-8')
        sock.close()

        assert "HTTP/1.1 200 OK" in response
        assert "Content-Type: text/plain" in response
        assert "vivic_total_packets_parsed" in response
        assert "vivic_anomalies_detected" in response
        assert "vivic_session_status" in response
    finally:
        exporter.stop()


def test_health_check_endpoint_reports_status():
    """Asserts that the cluster health endpoint responds with json initialization markers."""
    session = UnifiedVivicSession(port="MOCK_TEST_PORT")
    exporter = MetricsHttpExporter(session=session, host="127.0.0.1", port=18001)
    exporter.start()

    time.sleep(0.2)

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("127.0.0.1", 18001))
        sock.sendall(b"GET /health HTTP/1.1\r\nHost: localhost\r\n\r\n")
        response = sock.recv(4096).decode('utf-8')
        sock.close()

        assert "HTTP/1.1 503" in response or "HTTP/1.1 200" in response
        assert "application/json" in response
    finally:
        exporter.stop()
