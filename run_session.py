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
        print(f"[INIT] Launching mandatory {sweep_duration_seconds}-second ambient calibration sweep...")
        
        # HARDENING REMEDIATION: Dynamic Buffer Charging Safeguard.
        # If running a mock port profile, poll the active queue size until it passes the 1280 step
        # sliding window barrier. This ensures calibration matrices receive live wave vectors.
        if "MOCK" in self.adapter.daemon.port.upper() or "PORT" in self.adapter.daemon.port.upper():
            print(" -> Simulation track detected: Waiting for background buffer saturation (1280 frames)...")
            while True:
                with self.adapter.lock:
                    current_fill = len(self.adapter.buffers["ch1"])
                if current_fill >= self.adapter.window_size:
                    break
                print(f"    -> Charging registers: {current_fill}/{self.adapter.window_size} frames...", end="\r")
                time.sleep(0.2)
            print("\n -> Buffers fully charged. Accelerating calibration window down to 2.0 seconds.")
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

            # Pipe dynamic means and standard deviations directly into the train_step
            loss_val, latent_vector = self.engine.train_step(
                ambient_means=self.ambient_means, 
                ambient_stds=self.ambient_stds
            )

            if loss_val < 0.0 or latent_vector is None:
                print(f" -> [CYCLE {step}/{steps}] Buffer starvation fallback triggered. Waiting for data...")
                time.sleep(0.05)
                continue

            # Execute the 3-Sigma vector divergence metric monitoring tracking
            _ = self.monitor.evaluate_vector(latent_vector.cpu().numpy().flatten())

            # Trigger clear progress reporting and timing increments
            log_cycle_completion(step, steps)
            time.sleep(0.016)  # Maintain clean execution rate relative to our 60Hz ingestion

        self.is_active = False
        print("[SUCCESS] Operational session cycle completed cleanly.")

    def terminate_session(self):
        """Safely deactivates acquisition tracking lines cleanly."""
        print("[INFO] Shutting down orchestrated session tracks...")
        self.adapter.stop_acquisition()


if __name__ == "__main__":
    session = UnifiedVivicSession(port="MOCK")
    try:
        session.execute_baseline_calibration()
        session.execute_live_cycle(steps=5)
    except KeyboardInterrupt:
        print("\n[INFO] Manual interrupt override caught during active session run.")
    finally:
        session.terminate_session()
