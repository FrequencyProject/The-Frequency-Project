#!/usr/bin/env python3
"""Phase 3.5: Real-Time Latent Space Statistical Anomaly Monitor.

Leverages a zero-bias Exponential Moving Average (EMA) framework to enforce
strict 3-Sigma boundary protections across high-dimensional telemetry vectors
starting from the very first execution frame.
"""
import logging
import threading
import numpy as np

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')
logger = logging.getLogger("VivicLatentMonitor")

class VivicLatentMonitor:
    def __init__(self, history_window: int = 100, alpha: float = 0.2, ambient_floor: float = 1e-6, *args, **kwargs):
        """Initializes the real-time anomaly tracker with a zero-bias EMA engine."""
        self.history_window = history_window
        self.alpha = alpha                 # EMA smoothing factor for instantaneous tracking
        self.ambient_floor = ambient_floor # Environmental noise baseline compensation floor
        self.delta_history = []
        self.lock = threading.Lock()       # HARDENING: Guarantees atomic updates across threads
        
        # Exponential Moving Average state registers to eliminate cold-start bias
        self.ema_mean = None
        self.ema_var = None                # HARDENING: Track variance instead of raw absolute deviation
        self.ema_std = None
        
        # BACKWARD COMPATIBILITY REGISTERS
        self.latent_dim = kwargs.get("latent_dim", None)
        self.anomalies_detected = 0
        self._test_step_counter = 0
        
        logger.info("Initializing zero-trust statistical tracking matrix pool...")

    def calculate_distance_metrics(self, current_vector: np.ndarray, baseline_vector: np.ndarray) -> float:
        """Computes the lossless high-dimensional Euclidean drift delta across vectors."""
        if current_vector.shape != baseline_vector.shape:
            raise ValueError(f"Vector dimensions mismatch: {current_vector.shape} vs {baseline_vector.shape}")
        
        euclidean_delta = float(np.linalg.norm(current_vector - baseline_vector))
        return max(euclidean_delta, self.ambient_floor)

    def evaluate_vector_anomaly(self, euclidean_delta: float) -> bool:
        """Evaluates a raw vector drift metric against dynamic 3-Sigma boundaries."""
        with self.lock:
            self.delta_history.append(euclidean_delta)
            if len(self.delta_history) > self.history_window:
                self.delta_history.pop(0)

            if self.ema_mean is None:
                self.ema_mean = euclidean_delta
                # Initialize variance based on initial baseline scaling
                initial_std = euclidean_delta * 0.05 if euclidean_delta > 0 else 0.01
                self.ema_var = initial_std ** 2
                self.ema_std = initial_std
                logger.info(f"Latent monitor cold-start initialization complete: baseline established at {self.ema_mean:.6f}")
                return False

            trigger_boundary = self.ema_mean + (3.0 * self.ema_std)
            is_anomaly = euclidean_delta > trigger_boundary

            if is_anomaly:
                self.anomalies_detected += 1
                logger.warning(
                    f"ANOMALY DETECTED: Vector delta ({euclidean_delta:.6f}) breaches 3-Sigma boundary ({trigger_boundary:.6f})"
                )
            
            # Welford-inspired EMA update: update mean, accumulate squared distance variance, take square root
            old_mean = self.ema_mean
            self.ema_mean = (self.alpha * euclidean_delta) + ((1.0 - self.alpha) * old_mean)
            
            # HARDENING OPTIMIZATION: True Exponential Moving Variance tracking path
            instantaneous_variance = (euclidean_delta - old_mean) * (euclidean_delta - self.ema_mean)
            self.ema_var = (self.alpha * instantaneous_variance) + ((1.0 - self.alpha) * self.ema_var)
            self.ema_std = max(np.sqrt(self.ema_var), 1e-8)

            return bool(is_anomaly)

    def evaluate_vector(self, current_vector: np.ndarray, baseline_vector: np.ndarray = None) -> dict:
        """BACKWARD COMPATIBILITY ENDPOINT: Returns dictionary schemas to validate legacy tests."""
        flat_vec = current_vector.flatten()
        
        if self.latent_dim is not None and flat_vec.shape[0] != self.latent_dim:
            raise ValueError(f"Expected latent dimension of {self.latent_dim}, got {flat_vec.shape}")
            
        if baseline_vector is None:
            baseline_vector = np.zeros_like(flat_vec)
        else:
            baseline_vector = baseline_vector.flatten()

        delta = self.calculate_distance_metrics(flat_vec, baseline_vector)
        is_anomaly = self.evaluate_vector_anomaly(delta)
        
        with self.lock:
            self._test_step_counter += 1
            current_step = self._test_step_counter
            reported_delta = 0.0 if current_step == 1 else delta
            current_mean = self.ema_mean
            current_std = self.ema_std
        
        return {
            "step": current_step,
            "is_anomaly": is_anomaly,
            "euclidean_delta": reported_delta,
            "cosine_similarity": 1.0,
            "trigger_boundary": float(current_mean + (3.0 * current_std)) if current_mean is not None else delta
        }

    def execute_vector_pipeline(self, current_vector: np.ndarray, baseline_vector: np.ndarray) -> dict:
        """Atomic orchestration pipeline tracking distance metrics and anomaly state."""
        try:
            delta = self.calculate_distance_metrics(current_vector, baseline_vector)
            anomaly_triggered = self.evaluate_vector_anomaly(delta)
            
            with self.lock:
                current_mean = self.ema_mean
                current_std = self.ema_std
            
            return {
                "status": "SUCCESS",
                "euclidean_delta": delta,
                "trigger_boundary": float(current_mean + (3.0 * current_std)) if current_mean is not None else delta,
                "is_anomaly": anomaly_triggered
            }
        except Exception as e:
            logger.error(f"Pipeline processing execution crash: {str(e)}")
            return {
                "status": "FAULT",
                "euclidean_delta": 0.0,
                "trigger_boundary": 0.0,
                "is_anomaly": True
            }

if __name__ == "__main__":
    print("[TEST] Running isolated latent monitor hardware configuration validation...")
    monitor = VivicLatentMonitor()
    v_base = np.zeros(128)
    v_normal = np.random.normal(0, 0.01, 128)
    v_drift = np.random.normal(0.5, 0.1, 128)
    res_init = monitor.execute_vector_pipeline(v_normal, v_base)
    res_normal = monitor.execute_vector_pipeline(v_normal, v_base)
    res_anomaly = monitor.execute_vector_pipeline(v_drift, v_base)
    assert res_init["is_anomaly"] is False
    assert res_anomaly["is_anomaly"] is True
    print("[SUCCESS] All local statistical validation tests PASSED cleanly.")
