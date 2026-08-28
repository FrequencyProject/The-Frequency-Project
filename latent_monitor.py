#!/usr/bin/env python3
"""Phase 3.5: Real-Time Latent Space Statistical Anomaly Monitor.

Leverages a zero-bias Exponential Moving Average (EMA) framework to enforce
strict 3-Sigma boundary protections across high-dimensional telemetry vectors
starting from the very first execution frame.
"""
import logging
import numpy as np

# Setup localized engineering logging structures
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')
logger = logging.getLogger("VivicLatentMonitor")

class VivicLatentMonitor:
    def __init__(self, history_window: int = 100, alpha: float = 0.2, ambient_floor: float = 1e-6):
        """Initializes the real-time anomaly tracker with a zero-bias EMA engine."""
        self.history_window = history_window
        self.alpha = alpha                 # EMA smoothing factor for instantaneous tracking
        self.ambient_floor = ambient_floor # Environmental noise baseline compensation floor
        self.delta_history = []
        
        # Exponential Moving Average state registers to eliminate cold-start bias
        self.ema_mean = None
        self.ema_std = None
        
        logger.info("Initializing zero-trust statistical tracking matrix pool...")

    def calculate_distance_metrics(self, current_vector: np.ndarray, baseline_vector: np.ndarray) -> float:
        """Computes the lossless high-dimensional Euclidean drift delta across vectors."""
        if current_vector.shape != baseline_vector.shape:
            raise ValueError(f"Vector dimensions mismatch: {current_vector.shape} vs {baseline_vector.shape}")
        
        # Calculate true Euclidean distance across high-dimensional space
        euclidean_delta = float(np.linalg.norm(current_vector - baseline_vector))
        return max(euclidean_delta, self.ambient_floor)

    def evaluate_vector_anomaly(self, euclidean_delta: float) -> bool:
        """Evaluates a raw vector drift metric against dynamic 3-Sigma boundaries."""
        self.delta_history.append(euclidean_delta)
        if len(self.delta_history) > self.history_window:
            self.delta_history.pop(0)

        # CRITICAL HARDENING REFACTOR: Instantaneous initialization on the very first frame
        if self.ema_mean is None:
            self.ema_mean = euclidean_delta
            # Provide a safe initialization standard deviation window to prevent tight zero locks
            self.ema_std = euclidean_delta * 0.05 if euclidean_delta > 0 else 0.01
            logger.info(f"Latent monitor cold-start initialization complete: baseline established at {self.ema_mean:.6f}")
            return False  # First vector anchors the rolling baseline layer

        # Calculate the dynamic trigger boundary using our current 3-Sigma limits
        trigger_boundary = self.ema_mean + (3.0 * self.ema_std)
        is_anomaly = euclidean_delta > trigger_boundary

        if is_anomaly:
            logger.warning(
                f"ANOMALY DETECTED: Vector delta ({euclidean_delta:.6f}) breaches 3-Sigma boundary ({trigger_boundary:.6f})"
            )
        
        # Dynamically update our state tracking metrics using exponential decay curves
        # This prevents initialization noise from corrupting early field telemetry sweeps
        self.ema_mean = (self.alpha * euclidean_delta) + ((1 - self.alpha) * self.ema_mean)
        
        # Track variance changes smoothly to dynamically maintain stable standard deviations
        current_variance = abs(euclidean_delta - self.ema_mean)
        self.ema_std = (self.alpha * current_variance) + ((1 - self.alpha) * self.ema_std)

        return bool(is_anomaly)

    def execute_vector_pipeline(self, current_vector: np.ndarray, baseline_vector: np.ndarray) -> dict:
        """Atomic orchestration pipeline tracking distance metrics and anomaly state."""
        try:
            delta = self.calculate_distance_metrics(current_vector, baseline_vector)
            anomaly_triggered = self.evaluate_vector_anomaly(delta)
            
            return {
                "status": "SUCCESS",
                "euclidean_delta": delta,
                "trigger_boundary": float(self.ema_mean + (3.0 * self.ema_std)) if self.ema_mean is not None else delta,
                "is_anomaly": anomaly_triggered
            }
        except Exception as e:
            logger.error(f"Pipeline processing execution crash: {str(e)}")
            return {
                "status": "FAULT",
                "euclidean_delta": 0.0,
                "trigger_boundary": 0.0,
                "is_anomaly": True # Fail secure on internal script exceptions
            }

if __name__ == "__main__":
    # Standalone sanity testing layer verifying data tracking integrity
    print("[TEST] Running isolated latent monitor hardware configuration validation...")
    monitor = VivicLatentMonitor()
    
    # Generate dummy high-dimensional tracking states
    v_base = np.zeros(128)
    v_normal = np.random.normal(0, 0.01, 128)
    v_drift = np.random.normal(0.5, 0.1, 128) # Forces severe mathematical anomaly
    
    # Process test stream vectors
    res_init = monitor.execute_vector_pipeline(v_normal, v_base)
    res_normal = monitor.execute_vector_pipeline(v_normal, v_base)
    res_anomaly = monitor.execute_vector_pipeline(v_drift, v_base)
    
    assert res_init["is_anomaly"] is False, "Cold start baseline should register cleanly."
    assert res_anomaly["is_anomaly"] is True, "3-Sigma delta spike must trigger anomaly alert."
    print("[SUCCESS] All local statistical validation tests PASSED cleanly.")
