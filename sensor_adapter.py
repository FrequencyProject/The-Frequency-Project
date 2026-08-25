#!/usr/bin/env python3
"""Phase 2: Asynchronous Multi-Channel Sensor Adapter.

Bridges the bare-metal background HardwareSerialDaemon thread to rolling
memory deques with integrated per-channel error telemetry and performance diagnostics.
"""
from collections import deque
import threading
import time
import numpy as np
from serial_daemon import HardwareSerialDaemon
from spectral_processing import AsymmetricTensorPipeline


class MultiChannelSensorAdapter:
    """Manages thread-safe rolling queues, hardware daemon callbacks, and ingestion metrics."""

    def __init__(
        self,
        port: str = "COM3",
        baudrate: int = 115200,
        window_size: int = 1280,
        debug: bool = False,
    ):
        self.window_size = window_size
        self.debug = debug
        self._lock = threading.RLock()

        # Initialize independent thread-safe rolling deques for all 4 channels
        self.queues = {
            "ch1": deque(maxlen=window_size * 2),
            "ch2": deque(maxlen=window_size),
            "ch3": deque(maxlen=window_size),
            "ch4": deque(maxlen=window_size * 2),
        }

        # Lightweight, zero-dependency telemetry tracking metrics per path channel
        self.metrics = {
            "ch1_dropped": 0,
            "ch2_dropped": 0,
            "ch3_dropped": 0,
            "ch4_dropped": 0,
            "last_processing_time_ms": 0.0,
        }

        # Initialize the production pipeline compiler and bare-metal serial daemon
        self.pipeline = AsymmetricTensorPipeline()
        self.daemon = HardwareSerialDaemon(port=port, baudrate=baudrate)

        # Register the thread-safe callback handler to capture incoming vector frames
        self.daemon.register_callback(self.hardware_packet_callback)

    def hardware_packet_callback(self, vector: np.ndarray) -> None:
        """Thread-safe callback executed by the background serial daemon thread."""
        if vector is None or len(vector) != 4:
            return

        with self._lock:
            # Audit elements natively for non-finite values or corrupt drops prior to memory append
            if np.isnan(vector[0]) or np.isinf(vector[0]):
                self.metrics["ch1_dropped"] += 1
            else:
                self.queues["ch1"].append(vector[0])

            if np.isnan(vector[1]) or np.isinf(vector[1]):
                self.metrics["ch2_dropped"] += 1
            else:
                self.queues["ch2"].append(vector[1])

            if np.isnan(vector[2]) or np.isinf(vector[2]):
                self.metrics["ch3_dropped"] += 1
            else:
                self.queues["ch3"].append(vector[2])

            if np.isnan(vector[3]) or np.isinf(vector[3]):
                self.metrics["ch4_dropped"] += 1
            else:
                self.queues["ch4"].append(vector[3])

            if self.debug and any(self.metrics[f"ch{i}_dropped"] > 0 for i in range(1, 5)):
                print(f"[METRICS WARN] Active Drop Signatures Detected: {self.metrics}")

    def process_incoming_packet(self, packet_str: str) -> None:
        """Backward-compatibility bridge for test suites and string-based inputs."""
        vector = self.daemon.parse_raw_line(packet_str)
        if vector is not None:
            self.hardware_packet_callback(vector)

    def get_ai_features(self) -> np.ndarray:
        """Compiles and returns the unified normalized (4, 1280) float32 matrix tensor."""
        start_time = time.perf_counter()

        with self._lock:
            # Ensure the rolling spectral queues contain enough points before calculating transforms
            if len(self.queues["ch1"]) < self.window_size:
                return np.zeros((4, self.window_size), dtype=np.float32)

            ch1_raw = np.array(self.queues["ch1"])
            ch2_raw = np.array(self.queues["ch2"])
            ch3_raw = np.array(self.queues["ch3"])
            ch4_raw = np.array(self.queues["ch4"])

        # Process asymmetrically via the spectral pipeline
        tensor = self.pipeline.compile_feature_tensor(ch1_raw, ch2_raw, ch3_raw, ch4_raw)

        # Log high-resolution performance metrics natively to ensure execution remains low-overhead
        execution_time_ms = (time.perf_counter() - start_time) * 1000.0
        with self._lock:
            self.metrics["last_processing_time_ms"] = execution_time_ms

        return tensor

    def start_ingestion(self) -> None:
        """Spins up the underlying bare-metal background polling threads."""
        self.daemon.start()

    def stop_ingestion(self) -> None:
        """Gracefully halts the background physical hardware port acquisitions."""
        self.daemon.stop()


if __name__ == "__main__":
    print("[INIT] Verifying MultiChannelSensorAdapter observability tracking...")
    adapter = MultiChannelSensorAdapter(port="MOCK_PORT", debug=True)

    # Simulate data frames, including nan corruption vectors to test tracking telemetry
    adapter.hardware_packet_callback(np.array([1.0, np.nan, 3.0, 4.0], dtype=np.float32))

    assert adapter.metrics["ch2_dropped"] == 1
    assert len(adapter.queues["ch1"]) == 1
    print(f" -> Telemetry Mapping Validated. Active System Metrics: {adapter.metrics}")
    print("[SUCCESS] Low-overhead observability layer is fully functional.")
