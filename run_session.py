#!/usr/bin/env python3
"""Phase 5: Core Session Orchestration.

Manages continuous background ingestion cycles, data loops, and monitoring pipelines.
"""
import time
import torch
import numpy as np
from sensor_adapter import MultiChannelSensorAdapter
from train_engine import VivicTrainingEngine
from latent_monitor import VivicLatentMonitor


def log_ambient_baseline(ch: int, mean: float, std: float):
    """Outputs channel statistical baselines during environment calibration."""
    print(f"    -> [CH {ch}] Ambient Baseline: μ={mean:.4f}, σ={std:.4f}")


def log_cycle_completion(step: int, total: int):
    """Outputs optimization cycle progress tracking parameters."""
    print(f" -> [CYCLE {step}/{total}] Optimization Pass Complete.")


class UnifiedVivicSession:
    """Coordinates data extraction pipelines, baseline calibrations, and training updates."""

    def __init__(self, port: str = "MOCK"):
        self.adapter = MultiChannelSensorAdapter(port=port)
        self.engine = VivicTrainingEngine(port=port)
        self.is_active = False

        # Instantiates the statistical 3-Sigma latent space tracking module
        self.monitor = VivicLatentMonitor(latent_dim=128)

        # Ambient noise calibration registers tracking our four physical channels
        self.ambient_means = np.zeros(4, dtype=np.float32)
        self.ambient_stds = np.zeros(4, dtype=np.float32)
        self.is_calibrated = False

    def execute_baseline_calibration(
        self, sweep_duration_seconds: float = 120.0, sample_rate_hz: float = 100.0
    ):
        """Executes a non-blocking Quiet State Sweep to map native environment noise thresholds."""
        print(
            f"[INIT] Launching mandatory {sweep_duration_seconds}-second ambient calibration sweep..."
        )
        total_samples = int(sweep_duration_seconds * sample_rate_hz)

        # Pre-allocate calibration accumulation matrix for our 4 hardware channels
        calibration_buffer = []
        sample_interval = 1.0 / sample_rate_hz

        # Shorten sample collection duration if we are in a rapid simulation environment
        if "MOCK" in self.adapter.daemon.port.upper() or "PORT" in self.adapter.daemon.port.upper():
            print(
                " -> Simulation environment detected: Throttling calibration window to 2.0 seconds."
            )
            total_samples = int(2.0 * sample_rate_hz)

        for _ in range(total_samples):
            # Extract raw frame from sensor adapter matrices
            features = self.adapter.get_ai_features()
            # Reduce row-wise dimensions to extract instantaneous channel states
            if hasattr(features, "numpy"):
                channel_snapshots = features.mean(axis=1)
            else:
                channel_snapshots = np.mean(features, axis=1)
            calibration_buffer.append(channel_snapshots)
            time.sleep(sample_interval)

        # Compute dynamic statistical profiles across the accumulated sample history
        history_matrix = np.stack(calibration_buffer, axis=0)  # Shape: (samples, 4)

        for ch in range(4):
            self.ambient_means[ch] = history_matrix[:, ch].mean()
            self.ambient_stds[ch] = history_matrix[:, ch].std()
            # Enforce statistical epsilon boundary guards to prevent subsequent zero-division
            if self.ambient_stds[ch] < 1e-6:
                self.ambient_stds[ch] = 1e-6
            log_ambient_baseline(ch, self.ambient_means[ch], self.ambient_stds[ch])

        self.is_calibrated = True
        print("[SUCCESS] Dynamic baseline calibration completed. Environmental limits set.")

    def execute_live_cycle(self, steps: int = 5):
        """Runs consecutive pipeline loops, transforming waveforms into model adjustments."""
        if not self.is_calibrated:
            print("[WARNING] Session execution halted. Initializing auto-calibration fallback.")
            self.execute_baseline_calibration()

        print("[INIT] Launching orchestrated operational cycle...")
        self.is_active = True

        for step in range(1, steps + 1):
            if not self.is_active:
                break

            # Consume single-pass latent vectors returned directly by train_step()
            loss_val, latent_vector = self.engine.train_step()

            if loss_val < 0.0 or latent_vector is None:
                continue

            # Execute the 3-Sigma vector divergence metric monitoring tracking
            _ = self.monitor.evaluate_vector(latent_vector.detach().cpu().numpy())

            # Trigger clear progress reporting and timing increments
            log_cycle_completion(step, steps)
            time.sleep(0.01)

        self.is_active = False
        print("[SUCCESS] Operational session cycle completed cleanly.")


if __name__ == "__main__":
    session = UnifiedVivicSession(port="MOCK")
    session.execute_baseline_calibration()
    session.execute_live_cycle(steps=3)
    session.adapter.stop_acquisition()
