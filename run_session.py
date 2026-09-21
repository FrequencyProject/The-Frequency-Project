#!/usr/bin/env python3
"""Phase 5: Core Session Orchestration with Embedded Metrics Export.

Manages continuous background ingestion cycles, data loops, monitoring pipelines,
and hosts an independent thread-safe Prometheus/Health export endpoint.
"""
import time
import torch
import numpy as np
import signal
import sys
import json
import threading
import socket
from sensor_adapter import MultiChannelSensorAdapter
from train_engine import VivicTrainingEngine
from latent_monitor import VivicLatentMonitor


def emit_structured_log(event_type: str, level: str, msg: str, data: dict = None):
    """Outputs an atomic, machine-readable JSON logging packet to the stdout stream."""
    log_packet = {
        "timestamp": float(time.time()),
        "level": level,
        "component": "SessionOrchestrator",
        "event": event_type,
        "message": msg
    }
    if data:
        log_packet.update(data)
    print(json.dumps(log_packet), flush=True)


class MetricsHttpExporter(threading.Thread):
    """Hosts a minimal, lightweight, zero-dependency HTTP server for Prometheus scraping and health probes."""

    def __init__(self, session, host: str = "0.0.0.0", port: int = 8080):  # nosec B104
        super().__init__()
        self.session = session
        self.host = host
        self.port = port
        self.running = False
        self.daemon = True
        self.server_socket = None

    def run(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            emit_structured_log("METRICS_SERVER_STARTED", "INFO", f"HTTP Exporter active on http://{self.host}:{self.port}")
        except Exception as e:
            emit_structured_log("METRICS_SERVER_ERROR", "CRITICAL", f"Failed to bind HTTP Exporter: {str(e)}")
            return

        self.server_socket.settimeout(0.5)

        while self.running:
            try:
                client_sock, addr = self.server_socket.accept()
            except socket.timeout:
                continue
            except Exception:
                break

            try:
                request = client_sock.recv(1024).decode('utf-8', errors='ignore')
                if not request:
                    client_sock.close()
                    continue

                if "GET /health" in request:
                    status_code = "200 OK" if self.session.is_active or self.session.is_calibrated else "503 Service Unavailable"
                    body = json.dumps({"status": "HEALTHY" if "200" in status_code else "INITIALIZING"})
                    response = f"HTTP/1.1 {status_code}\r\nContent-Type: application/json\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n{body}"

                elif "GET /metrics" in request:
                    with self.session.metrics_lock:
                        body = (
                            f"# HELP vivic_total_packets_parsed Total telemetry packets processed\n"
                            f"# TYPE vivic_total_packets_parsed counter\n"
                            f"vivic_total_packets_parsed {self.session.adapter.daemon.frames_parsed if (hasattr(self.session, 'adapter') and self.session.adapter and self.session.adapter.daemon) else 0}\n"
                            f"# HELP vivic_total_packets_dropped Total telemetry packets dropped\n"
                            f"# TYPE vivic_total_packets_dropped counter\n"
                            f"vivic_total_packets_dropped {self.session.adapter.daemon.frames_dropped if (hasattr(self.session, 'adapter') and self.session.adapter and self.session.adapter.daemon) else 0}\n"
                            f"# HELP vivic_execution_cycles_total Total orchestrator algorithm loop cycles run\n"
                            f"# TYPE vivic_execution_cycles_total counter\n"
                            f"vivic_execution_cycles_total {self.session.total_cycles_run}\n"
                            f"# HELP vivic_anomalies_detected Total 3-Sigma structural anomalies captured\n"
                            f"# TYPE vivic_anomalies_detected counter\n"
                            f"vivic_anomalies_detected {self.session.anomalies_found}\n"
                            f"# HELP vivic_session_status Session operational status (0=inactive, 1=active, 2=calibrating)\n"
                            f"# TYPE vivic_session_status gauge\n"
                            f'vivic_session_status{{status="active"}} {1 if self.session.is_active else 0}\n'
                            f'vivic_session_status{{status="calibrated"}} {1 if self.session.is_calibrated else 0}\n'
                        )
                    response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain; version=0.0.4\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n{body}"

                else:
                    body = "Not Found"
                    response = f"HTTP/1.1 404 Not Found\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n{body}"

                client_sock.sendall(response.encode('utf-8'))
                client_sock.close()
            except Exception:
                pass

    def stop(self):
        """Cleanly terminates the socket connection link."""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass


class UnifiedVivicSession:
    """Coordinates data extraction pipelines, baseline calibrations, and training updates."""

    def __init__(self, port: str = "MOCK"):
        self.adapter = MultiChannelSensorAdapter(port=port)
        self.engine = VivicTrainingEngine(port=port, adapter=self.adapter)

        self.is_active = False
        self.monitor = VivicLatentMonitor(latent_dim=128)
        self.ambient_means = np.zeros(4, dtype=np.float32)
        self.ambient_stds = np.zeros(4, dtype=np.float32)
        self.is_calibrated = False

        self.metrics_lock = threading.Lock()
        self.total_cycles_run = 0
        self.anomalies_found = 0

    def execute_baseline_calibration(self, sweep_duration_seconds: float = 120.0, sample_rate_hz: float = 100.0):
        """Executes a non-blocking Quiet State Sweep to map native environment noise thresholds."""
        self.adapter.start_acquisition()
        emit_structured_log("CALIBRATION_START", "INFO", f"Launching mandatory {sweep_duration_seconds}-second ambient calibration sweep...")

        if "MOCK" in self.adapter.daemon.port.upper() or "PORT" in self.adapter.daemon.port.upper():
            emit_structured_log("SIMULATION_DETECTED", "INFO", "Simulation track detected: Waiting for background buffer saturation (1280 frames)...")
            while True:
                with self.adapter.lock:
                    current_fill = self.adapter._count
                if current_fill >= self.adapter.window_size:
                    break
                time.sleep(0.2)
            emit_structured_log("REGISTERS_CHARGED", "INFO", "Buffers fully charged. Accelerating calibration window down to 2.0 seconds.")
            sweep_duration_seconds = 2.0

        total_samples = int(sweep_duration_seconds * sample_rate_hz)
        calibration_buffer = []
        sample_interval = 1.0 / sample_rate_hz

        for _ in range(total_samples):
            features = self.adapter.get_raw_features()
            channel_snapshots = np.mean(features, axis=1)
            calibration_buffer.append(channel_snapshots)
            time.sleep(sample_interval)

        history_matrix = np.stack(calibration_buffer, axis=0)

        for ch in range(4):
            self.ambient_means[ch] = history_matrix[:, ch].mean()
            self.ambient_stds[ch] = history_matrix[:, ch].std()
            if self.ambient_stds[ch] < 1e-6:
                self.ambient_stds[ch] = 1e-6

        self.is_calibrated = True
        emit_structured_log("CALIBRATION_COMPLETE", "INFO", "Dynamic baseline calibration completed. Environmental limits set.")

    def execute_live_cycle(self, steps: int = 5):
        """Runs consecutive pipeline loops, transforming waveforms into model adjustments."""
        if not self.is_calibrated:
            self.execute_baseline_calibration()

        emit_structured_log("ORCHESTRATION_CYCLE_LAUNCH", "INFO", "Launching orchestrated operational cycle...")
        self.is_active = True

        for step in range(1, steps + 1):
            if not self.is_active:
                break

            loss_val, latent_vector = self.engine.train_step(
                ambient_means=self.ambient_means,
                ambient_stds=self.ambient_stds
            )

            if loss_val < 0.0 or latent_vector is None:
                time.sleep(0.05)
                continue

            is_anomaly = self.monitor.evaluate_vector(latent_vector.cpu().numpy().flatten())

            with self.metrics_lock:
                self.total_cycles_run += 1
                if isinstance(is_anomaly, dict) and is_anomaly.get("is_anomaly", False):
                    self.anomalies_found += 1

            time.sleep(0.016)

        self.is_active = False
        emit_structured_log("ORCHESTRATION_CYCLE_COMPLETE", "INFO", "Operational session cycle completed cleanly.")

    def terminate_session(self):
        """Safely deactivates acquisition tracking lines cleanly."""
        emit_structured_log("TEARDOWN", "INFO", "Shutting down orchestrated session tracks...")
        self.adapter.stop_acquisition()


if __name__ == "__main__":
    from verify_hardware_gate import execute_preflight_hardware_scan

    # Determine platform-specific hardware serial targets
    # Honor command line argument arrays if specified by the operator
    import argparse
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
    parser.add_index = False if hasattr(parser, "add_index") else None
    # Fallback to sys.argv parsing constraints cleanly
    passed_port = next((arg.split("=")[1] for arg in sys.argv if arg.startswith("--port=")), None)
    if not passed_port:
        passed_port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else None
    default_hardware_port = passed_port if passed_port else ("COM7" if sys.platform.startswith("win") else "/dev/ttyACM0")
    print(f"[ORCHESTRATOR] Cross-platform hardware probe targeted at: {default_hardware_port}")

    # Execute a strict, non-bypassed pre-flight connectivity check
    if execute_preflight_hardware_scan(target_port=default_hardware_port, max_discovery_wait_seconds=3.0):
        assigned_port = default_hardware_port
    else:
        print("[ORCHESTRATOR] Physical device un-verified. Reverting to structural mock track.")
        assigned_port = "MOCK"

    session = UnifiedVivicSession(port=assigned_port)

    exporter_server = MetricsHttpExporter(session=session, host="0.0.0.0", port=8080)  # nosec B104
    exporter_server.start()

    def handle_container_shutdown(signum, frame):
        emit_structured_log("SIGNAL_INTERCEPT", "WARNING", f"Container termination signal ({signum}) caught. Initiating graceful fallback shutdown...")
        session.is_active = False
        exporter_server.stop()
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, handle_container_shutdown)

    try:
        session.execute_baseline_calibration()
        session.execute_live_cycle(steps=5)
    except KeyboardInterrupt:
        emit_structured_log("INTERRUPT_CAUGHT", "INFO", "Manual or container interrupt override caught during active session run.")
    finally:
        exporter_server.stop()
        session.terminate_session()
