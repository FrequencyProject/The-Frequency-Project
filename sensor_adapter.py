#!/usr/bin/env python3
"""Phase 2: Cryptographically Hardened Multi-Channel Sensor Adapter.

Ingests signed telemetry packets, verifies origin authenticity via TPM 2.0 
public registries, and compiles secure rolling memory matrix deques.
"""
import time
from collections import deque
from typing import Tuple, Dict, Any
import numpy as np
from crypto_signer import HardwareTelemetrySigner
from serial_daemon import HardwareSerialDaemon


class MultiChannelSensorAdapter:
    """Consumes cryptographically signed packets and compiles row-normalized feature tensors."""

    def __init__(self, port: str = "COM3", window_size: int = 1280, debug: bool = False):
        self.window_size = window_size
        self.debug = debug

        # Allocate thread-safe rolling history deques for each isolated domain track
        self.ch1_buffer = deque(maxlen=2560)  # Spectral window depth requirement
        self.ch2_buffer = deque(maxlen=window_size)
        self.ch3_buffer = deque(maxlen=window_size)
        self.ch4_buffer = deque(maxlen=2560)  # Spectral window depth requirement

        # Performance metric counters and diagnostic indicator state tracks
        self.metrics: Dict[str, Any] = {
            "frames_received": 0,
            "frames_dropped_invalid_sig": 0,
            "last_processing_time_ms": 0.0,
        }

        # Initialize core cryptographic authentication nodes
        self.signer = HardwareTelemetrySigner()

        # Instantiate background serial hardware communication daemon path
        self.daemon = HardwareSerialDaemon(port=port)
        self.daemon.register_callback(self.process_signed_packet)

    def process_signed_packet(self, signed_packet: Tuple[bytes, bytes]) -> bool:
        """Intercepts, cryptographically authenticates, and unpacks signed telemetry frames."""
        payload_bytes, signature_bytes = signed_packet

        # Security Perimeter Check: Verify package was signed natively by local silicon hardware
        if not self.signer.verify_vector_signature(payload_bytes, signature_bytes):
            self.metrics["frames_dropped_invalid_sig"] += 1
            if self.debug:
                print("[SECURITY WARNING] Dropped unauthenticated data packet entry attempt.")
            return False

        # Cryptographic authenticity verified. Safely deserialize binary back to floats
        try:
            vector = np.frombuffer(payload_bytes, dtype=np.float32)
            if len(vector) != 4:
                return False

            self.metrics["frames_received"] += 1

            # Append values to their isolated channel rolling history queues
            self.ch1_buffer.append(vector[0])
            self.ch2_buffer.append(vector[1])
            self.ch3_buffer.append(vector[2])
            self.ch4_buffer.append(vector[3])
            return True

        except Exception:
            return False

    def get_ai_features(self) -> np.ndarray:
        """Extracts and balances multi-rate channel queues into a zero-mean feature array."""
        start_time = time.perf_counter()

        # Verify that all 4 discrete substrate deques contain sufficient operational samples
        if (
            len(self.ch1_buffer) < 2560
            or len(self.ch2_buffer) < self.window_size
            or len(self.ch3_buffer) < self.window_size
            or len(self.ch4_buffer) < 2560
        ):
            return np.zeros((4, self.window_size), dtype=np.float32)

        # Convert state queues to standalone floating point memory arrays
        ch1_raw = np.array(list(self.ch1_buffer), dtype=np.float32)
        ch2_raw = np.array(list(self.ch2_buffer), dtype=np.float32)
        ch3_raw = np.array(list(self.ch3_buffer), dtype=np.float32)
        ch4_raw = np.array(list(self.ch4_buffer), dtype=np.float32)

        # To maintain strict structural compatibility, we cross-link spectral processing
        # transformations natively. We import locally here to prevent circular import loops.
        from spectral_processing import AsymmetricTensorPipeline

        pipeline = AsymmetricTensorPipeline()

        normalized_tensor = pipeline.compile_feature_tensor(ch1_raw, ch2_raw, ch3_raw, ch4_raw)

        # Profile system performance execution parameters in milliseconds
        self.metrics["last_processing_time_ms"] = (time.perf_counter() - start_time) * 1000.0
        return normalized_tensor

    def start_ingestion(self) -> None:
        """Launches the underlying background thread collection loop loops."""
        self.daemon.start()

    def stop_ingestion(self) -> None:
        """Safely stops hardware serial port polling loops cleanly."""
        self.daemon.stop()


if __name__ == "__main__":
    print("[INIT] Verifying Hardened Multi-Channel Sensor Adapter integrity metrics...")
    adapter = MultiChannelSensorAdapter(port="MOCK", debug=True)

    # Simulate a signed hardware data transmission frame package natively
    mock_vector = np.array([1.1, 2.2, 3.3, 4.4], dtype=np.float32)
    p_bytes, s_bytes = adapter.signer.sign_vector(mock_vector)

    success = adapter.process_signed_packet((p_bytes, s_bytes))
    print(f" -> Processed Signed Ingestion Packet: {'[SUCCESS]' if success else '[FAILED]'}")
    assert success is True

    print(f" -> Active Buffer Metrics Captured   : {adapter.metrics}")
    print("[SUCCESS] Multi-Channel Ingestion validation architecture complete.")
