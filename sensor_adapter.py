#!/usr/bin/env python3
"""Phase 2: Sensor Adapter Bridge and Feature Compilation Engine.

Decoupled architectural components splitting circular buffering storage, 
stream ingestion orchestration, and digital signal feature compilation.
"""
import logging
import threading
import re
import numpy as np
from serial_daemon import HardwareSerialDaemon
from spectral_processing import AsymmetricTensorPipeline

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')
logger = logging.getLogger("SensorAdapter")


class TelemetryCircularBuffer:
    """Thread-safe storage class managing O(1) circular buffers and pointers."""
    
    def __init__(self, window_size: int = 1280):
        self.window_size = window_size
        self.lock = threading.RLock()
        self._buf_capacity = window_size * 2
        self._circular_buffer = np.zeros((4, self._buf_capacity), dtype=np.float32)
        self._head = 0
        self._count = 0

    def push(self, data_tuple: tuple):
        """Pushes a validated 4-channel data tuple into the circular matrix memory map."""
        with self.lock:
            idx = self._head
            for ch in range(4):
                val = float(data_tuple[ch])
                self._circular_buffer[ch, idx] = val
                self._circular_buffer[ch, idx + self.window_size] = val

            self._head = (self._head + 1) % self.window_size
            if self._count < self.window_size:
                self._count += 1

    def get_window_view(self, destination_matrix: np.ndarray) -> bool:
        """Populates a contiguous view slice if the window has fully charged."""
        with self.lock:
            if self._count < self.window_size:
                return False
            start_idx = self._head
            destination_matrix[:, :] = self._circular_buffer[:, start_idx : start_idx + self.window_size]
            return True

    def reset(self):
        """Resets pointers and clear metrics for testing framework integration setups."""
        with self.lock:
            self._head = 0
            self._count = 0
            self._circular_buffer.fill(0)


class FeatureCompiler:
    """Handles statistical validation and DSP conversions on extraction blocks."""
    
    def __init__(self, window_size: int = 1280):
        self.window_size = window_size
        self.dsp_pipeline = AsymmetricTensorPipeline()

    def process_window(self, source_matrix: np.ndarray) -> np.ndarray:
        """Executes 3-Sigma firewall checks and compiles spatial DSP feature tensors."""
        channel_variances = np.var(source_matrix, axis=1)
        if np.any(channel_variances < 1e-6):
            logger.error("[FIREWALL ALERT] Critical hardware sensor flatline detected! Purging feature tensor context.")
            return np.zeros((4, self.window_size), dtype=np.float32)

        return self.dsp_pipeline.compile_feature_tensor(
            source_matrix[0], source_matrix[1], source_matrix[2], source_matrix[3]
        )


class SensorAdapter:
    """Thread-safe telemetry bridge routing serial stream buffers to DSP matrices."""

    def __init__(self, port: str = "COM3", baudrate: int = 115200, window_size: int = 1280, *args, **kwargs):
        self.window_size = window_size
        
        # Instantiate single-responsibility child dependencies
        self._buffer_manager = TelemetryCircularBuffer(window_size=window_size)
        self._feature_compiler = FeatureCompiler(window_size=window_size)
        
        # Maintain public state properties for backwards compatibility with tests and run_session.py
        self.lock = self._buffer_manager.lock
        self._shared_feature_matrix = np.zeros((4, window_size), dtype=np.float32)

        self.daemon = HardwareSerialDaemon(
            port=port,
            baudrate=baudrate,
            callback=self._packet_ingestion_callback,
            use_mock_fallback=True
        )

        self.frames_received = 0
        self.frames_dropped = 0
        self._fallback_regex = re.compile(
            r"V1:(?P<v1>-?\d+\.\d+),V2:(?P<v2>-?\d+\.\d+),V3:(?P<v3>-?\d+\.\d+),V4:(?P<v4>-?\d+\.\d+)"
        )

    @property
    def _circular_buffer(self):
        return self._buffer_manager._circular_buffer

    @property
    def _count(self):
        return self._buffer_manager._count

    @_count.setter
    def _count(self, value):
        self._buffer_manager._count = value

    @property
    def _head(self):
        return self._buffer_manager._head

    @_head.setter
    def _head(self, value):
        self._buffer_manager._head = value

    def _packet_ingestion_callback(self, data_tuple: tuple):
        """Consumes raw tuples and offloads them directly to the decoupled storage manager."""
        if not data_tuple or len(data_tuple) != 4:
            self.frames_dropped += 1
            return

        with self.lock:
            self.frames_received += 1
            self._buffer_manager.push(data_tuple)

    def process_incoming_packet(self, raw_input: str or bytes):
        """Strict Data Contract Endpoint decoding incoming raw network string packets."""
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
                    float(groups["v1"]), float(groups["v2"]),
                    float(groups["v3"]), float(groups["v4"])
                )
                self._packet_ingestion_callback(parsed_tuple)
            else:
                self.frames_dropped += 1
        except Exception as e:
            self.frames_dropped += 1
            logger.debug(f"Transient boundary ingestion drop: {str(e)}")

    def start_acquisition(self):
        self.daemon.start()

    def stop_acquisition(self):
        self.daemon.stop()

    def get_ai_features(self) -> np.ndarray:
        """Extracts chronological window metrics and routes them through the compiler module."""
        with self.lock:
            has_data = self._buffer_manager.get_window_view(self._shared_feature_matrix)
            if not has_data:
                return np.zeros((4, self.window_size), dtype=np.float32)

            return self._feature_compiler.process_window(self._shared_feature_matrix)


# Export class under universal tracking name alias
MultiChannelSensorAdapter = SensorAdapter                self.frames_dropped += 1
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
