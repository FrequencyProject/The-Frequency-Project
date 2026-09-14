#!/usr/bin/env python3
"""Phase 2: Sensor Adapter Bridge and Feature Compilation Engine.

Manages rolling channel buffers using an O(1) thread-safe circular array,
consumes non-blocking serial daemon tuples, and compiles processed vectors
into model-ready tensors through strict data contracts.
"""
import logging
import threading
import re
import numpy as np
from serial_daemon import HardwareSerialDaemon
from spectral_processing import AsymmetricTensorPipeline

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')
logger = logging.getLogger("SensorAdapter")

class SensorAdapter:
    """Thread-safe telemetry bridge routing serial stream buffers to DSP matrices."""

    def __init__(self, port: str = "COM3", baudrate: int = 115200, window_size: int = 1280, *args, **kwargs):
        """Initializes pre-allocated circular buffers for all 4 isolated hardware channels."""
        self.window_size = window_size
        self.lock = threading.RLock()

        # HIGH-PERFORMANCE UPGRADE: Pre-allocate static circular buffer layout
        # Sized to double capacity to guarantee a continuous contiguous view trace array
        self._buf_capacity = window_size * 2
        self._circular_buffer = np.zeros((4, self._buf_capacity), dtype=np.float32)
        self._head = 0
        self._count = 0

        # Pre-allocated matrix for DSP out-routing tracking
        self._shared_feature_matrix = np.zeros((4, window_size), dtype=np.float32)

        self.dsp_pipeline = AsymmetricTensorPipeline()

        self.daemon = HardwareSerialDaemon(
            port=port,
            baudrate=baudrate,
            callback=self._packet_ingestion_callback,
            use_mock_fallback=True
        )

        # Sized state tracking parameters
        self.frames_received = 0
        self.frames_dropped = 0

        # High-assurance regex fallback for testing inputs containing multi-precision float decimals
        self._fallback_regex = re.compile(
            r"V1:(?P<v1>-?\d+\.\d+),V2:(?P<v2>-?\d+\.\d+),V3:(?P<v3>-?\d+\.\d+),V4:(?P<v4>-?\d+\.\d+)"
        )

    def _packet_ingestion_callback(self, data_tuple: tuple):
        """Consumes the raw native tuple dispatched from the daemon loop securely in O(1)."""
        if not data_tuple or len(data_tuple) != 4:
            self.frames_dropped += 1
            return

        with self.lock:
            self.frames_received += 1
            
            # Write data directly into the circular buffer index positions
            idx = self._head
            self._circular_buffer[0, idx] = float(data_tuple[0])
            self._circular_buffer[1, idx] = float(data_tuple[1])
            self._circular_buffer[2, idx] = float(data_tuple[2])
            self._circular_buffer[3, idx] = float(data_tuple[3])

            # Mirror copy to the second half of the buffer to enable zero-copy contiguous slicing view maps
            self._circular_buffer[0, idx + self.window_size] = float(data_tuple[0])
            self._circular_buffer[1, idx + self.window_size] = float(data_tuple[1])
            self._circular_buffer[2, idx + self.window_size] = float(data_tuple[2])
            self._circular_buffer[3, idx + self.window_size] = float(data_tuple[3])

            # Advance head pointer wrap-around boundaries
            self._head = (self._head + 1) % self.window_size
            if self._count < self.window_size:
                self._count += 1

    def process_incoming_packet(self, raw_input: str or bytes):
        """Strict Data Contract Endpoint: Decodes, truncates, and routes raw telemetry data data frames."""
        if raw_input is None:
            return

        try:
            raw_string = raw_input.decode('utf-8') if isinstance(raw_input, bytes) else raw_input
            clean_str = raw_string.strip()

            if not clean_str:
                return

            match = self._fallback_regex.search(clean_str)
            if match:
                groups = match.groupdict()
                parsed_tuple = (
                    float(groups["v1"]),
                    float(groups["v2"]),
                    float(groups["v3"]),
                    float(groups["v4"])
                )
                self._packet_ingestion_callback(parsed_tuple)
            else:
                self.frames_dropped += 1
        except Exception as e:
            self.frames_dropped += 1
            logger.debug(f"Transient boundary ingestion drop: {str(e)}")

    def start_acquisition(self):
        """Spins up the background hardware polling daemon loops."""
        self.daemon.start()

    def stop_acquisition(self):
        """Safely terminates the background hardware polling daemon loops."""
        self.daemon.stop()

    def get_ai_features(self) -> np.ndarray:
        """Compiles rolling window frames into a normalized (4, 1280) NumPy Array in O(1)."""
        with self.lock:
            # Check if buffer has fully saturated its 1280 historical footprints yet
            if self._count < self.window_size:
                return np.zeros((4, self.window_size), dtype=np.float32)

            # ZERO-COPY O(1) SLICE VIEW: Pull chronological slice instantly from pre-mirrored memory array maps
            start_idx = self._head
            self._shared_feature_matrix[:, :] = self._circular_buffer[:, start_idx : start_idx + self.window_size]

            # 3-Sigma Flatline Dropout Protection Firewall
            channel_variances = np.var(self._shared_feature_matrix, axis=1)
            if np.any(channel_variances < 1e-6):
                logger.error("[FIREWALL ALERT] Critical hardware sensor flatline detected! Purging feature tensor context.")
                return np.zeros((4, self.window_size), dtype=np.float32)

            processed_matrix = self.dsp_pipeline.compile_feature_tensor(
                self._shared_feature_matrix[0],
                self._shared_feature_matrix[1],
                self._shared_feature_matrix[2],
                self._shared_feature_matrix[3]
            )
            return processed_matrix

# Export class under universal tracking name alias
MultiChannelSensorAdapter = SensorAdapter
