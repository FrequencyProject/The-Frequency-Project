#!/usr/bin/env python3
"""Phase 5: Core Session Orchestration.

Manages continuous background ingestion cycles, data loops, and monitoring pipelines.
"""
import time
import torch
import numpy as np
# HARDENING REMEDIATION: Import native POSIX signal interface to trap container terminations
import signal
import sys
# HARDENING REMEDIATION: Import native json serialization to compile logs into structured arrays
import json
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
    # Output as a single-line JSON payload to guarantee atomicity for log aggregators
    print(json.dumps(log_packet), flush=True)


def log_ambient_baseline(ch: int, mean: float, std: float):
    """Outputs channel statistical baselines during environment calibration as structured JSON."""
    emit_structured_log(
        event_type="CALIBRATION_CHANNEL_SNAPSHOT",
        level="INFO",
        msg=f"Ambient Baseline established for channel {ch}",
        data={"channel": ch, "ambient_mean": float(mean), "ambient_std": float(std)}
    )


def log_cycle_completion(step: int, total: int):
    """Outputs optimization cycle progress tracking parameters as structured JSON."""
    emit_structured_log(
        event_type="OPTIMIZATION_PASS_COMPLETE",
        level="INFO",
        msg=f"Optimization Cycle {step}/{total} processed successfully",
        data={"cycle_step": step, "cycle_total": total}
    )


class UnifiedVivicSession:
    """Coordinates data extraction pipelines, baseline calibrations, and training updates."""

    def __init__(self, port: str = "MOCK"):
        # Shared core adapter layout to prevent dual-initialization port collisions
        self.adapter = MultiChannelSensorAdapter(port=port)
        self.engine = VivicTrainingEngine(port=port)
        self.engine.adapter = self.adapter
        
        self.is_active = False

        # Instantiates the statistical 3-Sigma latent space tracking module
        self.monitor = VivicLatentMonitor(latent_dim=128)

        # Ambient noise calibration registers tracking our four physical channels
        self.ambient_means = np.zeros(4, dtype=np.float32)
        self.ambient_stds = np.zeros(4, dtype=np.float32)
        self.is_calibrated = False

    def execute_baseline_calibration(self, sweep_duration_seconds: float = 120.0, sample_rate_hz: float = 100.0):
        """Executes a non-blocking Quiet State Sweep to map native environment noise thresholds."""
        self.adapter.start_acquisition()
        emit_structured_log("CALIBRATION_START", "INFO", f"Launching mandatory {sweep_duration_seconds}-second ambient calibration sweep...")
        
        # HARDENING REMEDIATION: Dynamic Buffer Charging Safeguard.
        # If running a mock port profile, poll the active queue size until it passes the 1280 step
        # sliding window barrier. This ensures calibration matrices receive live wave vectors.
        if "MOCK" in self.adapter.daemon.port.upper() or "PORT" in self.adapter.daemon.port.upper():
            emit_structured_log("SIMULATION_DETECTED", "INFO", "Simulation track detected: Waiting for background buffer saturation (1280 frames)...")
            while True:
                with self.adapter.lock:
                    current_fill = len(self.adapter.buffers["ch1"])
                if current_fill >= self.adapter.window_size:
                    break
                time.sleep(0.2)
            emit_structured_log("REGISTERS_CHARGED", "INFO", "Buffers fully charged. Accelerating calibration window down to 2.0 seconds.")
            sweep_duration_seconds = 2.0

        total_samples = int(sweep_duration_seconds * sample_rate_hz)
        calibration_buffer = []
        sample_interval = 1.0 / sample_rate_hz

        for _ in range(total_samples):
            features = self.adapter.get_ai_features()
            channel_snapshots = np.mean(features, axis=1)
            calibration_buffer.append(channel_snapshots)
            time.sleep(sample_interval)

        # Compute dynamic statistical profiles across the accumulated sample history
        history_matrix = np.stack(calibration_buffer, axis=0)  # Shape: (samples, 4)

        for ch in range(4):
            self.ambient_means[ch] = history_matrix[:, ch].mean()
            self.ambient_stds[ch] = history_matrix[:, ch].std()
            if self.ambient_stds[ch] < 1e-6:
                self.ambient_stds[ch] = 1e-6
            log_ambient_baseline(ch, self.ambient_means[ch], self.ambient_stds[ch])

        self.is_calibrated = True
        emit_structured_log("CALIBRATION_COMPLETE", "INFO", "Dynamic baseline calibration completed. Environmental limits set.")

    def execute_live_cycle(self, steps: int = 5):
        """Runs consecutive pipeline loops, transforming waveforms into model adjustments."""
        if not self.is_calibrated:
            emit_structured_log("AUTO_CALIBRATION_FALLBACK", "WARNING", "Session execution halted. Initializing auto-calibration fallback.")
            self.execute_baseline_calibration()

        emit_structured_log("ORCHESTRATION_CYCLE_LAUNCH", "INFO", "Launching orchestrated operational cycle...")
        self.is_active = True

        for step in range(1, steps + 1):
            if not self.is_active:
                break

            # Pipe dynamic means and standard deviations directly into the train_step
            loss_val, latent_vector = self.engine.train_step(
                ambient_means=self.ambient_means, 
                ambient_stds=self.ambient_stds
            )

            if loss_val < 0.0 or latent_vector is None:
                emit_structured_log("BUFFER_STARVATION", "WARNING", f"Cycle {step}/{steps} buffer starvation fallback triggered. Waiting for data...")
                time.sleep(0.05)
                continue

            # Execute the 3-Sigma vector divergence metric monitoring tracking
            _ = self.monitor.evaluate_vector(latent_vector.cpu().numpy().flatten())

            # Trigger clear progress reporting and timing increments
            log_cycle_completion(step, steps)
            time.sleep(0.016)  # Maintain clean execution rate relative to our 60Hz ingestion

        self.is_active = False
        emit_structured_log("ORCHESTRATION_CYCLE_COMPLETE", "INFO", "Operational session cycle completed cleanly.")

    def terminate_session(self):
        """Safely deactivates acquisition tracking lines cleanly."""
        emit_structured_log("TEARDOWN", "INFO", "Shutting down orchestrated session tracks...")
        self.adapter.stop_acquisition()


if __name__ == "__main__":
    session = UnifiedVivicSession(port="MOCK")
    
    # HARDENING REMEDIATION: Clean Container Lifecycle Signal Interceptor.
    # Traps standard SIGTERM (Docker container stop) signals natively and routes
    # them straight into our graceful cleanup taxonomy to protect hardware threads.
    def handle_container_shutdown(signum, frame):
        emit_structured_log("SIGNAL_INTERCEPT", "WARNING", f"Container termination signal ({signum}) caught. Initiating graceful fallback shutdown...")
        session.is_active = False
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, handle_container_shutdown)

    try:
        session.execute_baseline_calibration()
        session.execute_live_cycle(steps=5)
    except KeyboardInterrupt:
        emit_structured_log("INTERRUPT_CAUGHT", "INFO", "Manual or container interrupt override caught during active session run.")
    finally:
        session.terminate_session()
