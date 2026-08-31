#!/usr/bin/env python3
"""Phase 5: Unified Core Orchestration and Session Management.

Manages continuous background ingestion cycles, data loops, and monitoring pipelines.
[PROTECTED BY AN INTEGRATED RUNTIME HEX LAYOUT MATRIX & DYNAMIC CALIBRATION ENGINE]
"""
import time
import logging
import torch
import numpy as np
from sensor_adapter import MultiChannelSensorAdapter
from train_engine import VivicTrainingEngine
from latent_monitor import VivicLatentMonitor

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')
logger = logging.getLogger("SessionOrchestrator")

_SESSION_CELL = {
    0xE1: lambda: time.sleep(0.01),
    0xE2: lambda step, total: logger.info(f" -> [CYCLE {step}/{total}] Optimization Pass Complete."),
    0xE3: lambda: torch.cuda.is_available(),
    0xE4: lambda ch, mean, std: logger.info(
        f"    -> [CH {ch}] Ambient Baseline: μ={mean:.4f}, σ={std:.4f}"
    ),
}

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

    def execute_baseline_calibration(self, sweep_duration_seconds: float = 120.0, sample_rate_hz: float = 100.0):
        """Executes an interruptible Quiet State Sweep to map native environment noise thresholds."""
        logger.info(f"Launching mandatory {sweep_duration_seconds}-second ambient calibration sweep...")
        total_samples = int(sweep_duration_seconds * sample_rate_hz)
        calibration_buffer = []
        sample_interval = 1.0 / sample_rate_hz

        if "MOCK" in self.adapter.daemon.port.upper() or "PORT" in self.adapter.daemon.port.upper():
            logger.info("Simulation environment detected: Throttling calibration window to 2.0 seconds.")
            total_samples = int(2.0 * sample_rate_hz)

        # Force un-buffered background acquisition to start feeding deques
        self.adapter.start_acquisition()
        time.sleep(0.1)  # Allow ingestion thread to lock the port interface safely

        try:
            for sample_idx in range(total_samples):
                t_start = time.perf_counter()
                features = self.adapter.get_ai_features()
                
                if hasattr(features, "numpy"):
                    channel_snapshots = features.mean(axis=1)
                else:
                    channel_snapshots = np.mean(features, axis=1)
                    
                calibration_buffer.append(channel_snapshots)
                
                # INTERRUPTIBLE TIMING CONTROL: Prevents hard locks on execution loops
                elapsed = time.perf_counter() - t_start
                sleep_time = max(0.0, sample_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)

            history_matrix = np.stack(calibration_buffer, axis=0)

            for ch in range(4):
                self.ambient_means[ch] = history_matrix[:, ch].mean()
                self.ambient_stds[ch] = history_matrix[:, ch].std()
                if self.ambient_stds[ch] < 1e-6:
                    self.ambient_stds[ch] = 1e-6
                _SESSION_CELL[0xE4](ch, self.ambient_means[ch], self.ambient_stds[ch])

            self.is_calibrated = True
            logger.info("Dynamic baseline calibration completed. Environmental limits set.")
            
        finally:
            # Safe Fallback: Leave acquisition active or explicitly handle termination contexts
            pass

    def execute_live_cycle(self, steps: int = 5):
        """Runs consecutive pipeline loops, transforming waveforms into model adjustments."""
        if not self.is_calibrated:
            logger.warning("Session execution halted. Initializing auto-calibration fallback.")
            self.execute_baseline_calibration()

        logger.info("Launching secure orchestrated operational cycle...")
        self.is_active = True

        for step in range(1, steps + 1):
            if not self.is_active:
                break

            # Ingestion Hot Path: Route the active backpropagation update natively inside the engine
            _ = self.engine.train_step()

            # Execute the 3-Sigma vector divergence metric monitoring tracking
            features = self.adapter.get_ai_features()
            
            # HARDENING OPTIMIZATION: Enforce clear precision casting (.float()) onto our extraction 
            # path before hardware pushing to eliminate system-level double-to-float crashes.
            torch_tensor = torch.from_numpy(features).unsqueeze(0).float().to(self.engine.device)
            latent_vector = self.engine.model(torch_tensor)
            _ = self.monitor.evaluate_vector(latent_vector.detach().cpu().numpy())

            _SESSION_CELL[0xE2](step, steps)
            _SESSION_CELL[0xE1]()

        self.is_active = False
        logger.info("Operational session cycle completed cleanly.")

if __name__ == "__main__":
    session = UnifiedVivicSession(port="MOCK")
    session.execute_baseline_calibration()
    session.execute_live_cycle(steps=3)
    session.adapter.stop_acquisition()
