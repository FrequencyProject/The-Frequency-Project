#!/usr/bin/env python3
"""Phase 2: Sensor Adapter Bridge and Feature Compilation Engine.

Manages rolling channel buffers, consumes non-blocking serial daemon tuples,
and compiles processed vectors into model-ready tensors through strict data contracts.
"""
import collections
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
        """Initializes rolling double-ended queues for all 4 isolated hardware channels."""
        self.window_size = window_size
        self.lock = threading.RLock()
        
        self.buffers = {
            "ch1": collections.deque(maxlen=window_size),
            "ch2": collections.deque(maxlen=window_size),
            "ch3": collections.deque(maxlen=window_size),
            "ch4": collections.deque(maxlen=window_size),
        }
        
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
        """Consumes the raw native tuple dispatched from the daemon loop."""
        if not data_tuple or len(data_tuple) != 4:
            self.frames_dropped += 1
            return

        with self.lock:
            self.frames_received += 1
            # Distribute channel values to their respective buffers as a 1D sequence over time
            self.buffers["ch1"].append(float(data_tuple[0]))
            self.buffers["ch2"].append(float(data_tuple[1]))
            self.buffers["ch3"].append(float(data_tuple[2]))
            self.buffers["ch4"].append(float(data_tuple[3]))

    def process_incoming_packet(self, raw_input: str or bytes):
        """Strict Data Contract Endpoint: Decodes, truncates, and routes raw telemetry data frames."""
        if raw_input is None:
            return

        try:
            # Decode incoming bytes or strings natively
            raw_string = raw_input.decode('utf-8') if isinstance(raw_input, bytes) else raw_input
            clean_str = raw_string.strip()
            
            if not clean_str:
                return

            # Check if input line matches our flexible precision parser fallback matrix
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
        """Compiles rolling window frames into a normalized (4, 1280) NumPy Array."""
        with self.lock:
            if any(len(self.buffers[ch]) < self.window_size for ch in ["ch1", "ch2", "ch3", "ch4"]):
                return np.zeros((4, self.window_size), dtype=np.float32)

            ch1_arr = np.array(self.buffers["ch1"], dtype=np.float32)
            ch2_arr = np.array(self.buffers["ch2"], dtype=np.float32)
            ch3_arr = np.array(self.buffers["ch3"], dtype=np.float32)
            ch4_arr = np.array(self.buffers["ch4"], dtype=np.float32)

        # Process aligned rows through the active DSP matrix compiler layers
        processed_matrix = self.dsp_pipeline.compile_feature_tensor(ch1_arr, ch2_arr, ch3_arr, ch4_arr)
        return processed_matrix

# Export class under universal tracking name alias
MultiChannelSensorAdapter = SensorAdapter
