#!/usr/bin/env python3
"""Unified Phase 2 Hardware Serial Ingestion Daemon.

Combines strict regex validation checks with non-blocking threading,
automatic port reconnection logic, and thread-safe sliding window matrix scaling.
"""
import time
import threading
import re
import numpy as np
import serial
from spectral_processing import AsymmetricTensorPipeline


class ResilientSerialDaemon:
    """Manages background serial port acquisition with strict syntax validation checks."""

    def __init__(self, port: str = "MOCK", baudrate: int = 115200, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout

        # Operational Thread Control Flags
        self.is_running = False
        self._thread = None
        self._lock = threading.Lock()

        # Telemetry Diagnostics Counters
        self.frames_received = 0
        self.frames_dropped = 0

        # Ingestion Hardware Array Buffers
        self.ch1_buffer = []
        self.ch2_buffer = []
        self.ch3_buffer = []
        self.ch4_buffer = []

        # Pre-compile your exact syntax verification pattern for optimal performance
        self.packet_pattern = re.compile(
            r"^V1:([+-]?\d+\.?\d*),V2:([+-]?\d+\.?\d*),V3:([+-]?\d+\.?\d*),V4:([+-]?\d+\.?\d*)"
        )

        # Initialize Core Spectral Transformation Engine
        self.pipeline = AsymmetricTensorPipeline()
        self.latest_tensor = np.zeros((4, 1280), dtype=np.float32)

    def start(self):
        """Spins up the non-blocking hardware ingestion background worker loop."""
        with self._lock:
            if self.is_running:
                return
            self.is_running = True
            self._thread = threading.Thread(target=self._worker_loop, daemon=True)
            self._thread.start()
            print(f"[INIT] Unified Serial Daemon initialized on port: {self.port}")

    def stop(self):
        """Safely signals the thread loop to terminate and releases the physical port connection."""
        with self._lock:
            self.is_running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            print("[SHUTDOWN] Serial Daemon background threads safely disengaged.")

    def _worker_loop(self):
        """Continuous internal thread worker managing connection states and string splits."""
        ser = None
        while self.is_running:
            if self.port.upper() == "MOCK":
                self._generate_mock_frame()
                time.sleep(0.01)
                continue

            if ser is None or not ser.is_open:
                try:
                    ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
                    ser.reset_input_buffer()
                    print(f"[HARDWARE] Serial communication established over port: {self.port}")
                except Exception as err:
                    print(
                        f"[CONN_WAIT] Port {self.port} unavailable: {repr(err)}. Retrying in 3s..."
                    )
                    time.sleep(3.0)
                    continue

            try:
                if ser.in_waiting > 0:
                    raw_line = ser.readline()
                    decoded_line = raw_line.decode("utf-8", errors="ignore").strip()
                    if decoded_line:
                        self._process_packet_string(decoded_line)
            except Exception as err:
                print(
                    f"[BUS_ERR] Ingestion loop hit a hardware drop: {repr(err)}. Re-initializing tracking bus..."
                )
                if ser:
                    try:
                        ser.close()
                    except:
                        pass
                ser = None
                time.sleep(1.0)

    def _process_packet_string(self, packet_str: str):
        """Validates incoming telemetry frames using your pre-compiled regex engine patterns."""
        match = self.packet_pattern.match(packet_str)
        if not match:
            with self._lock:
                self.frames_dropped += 1
            return  # Safely filter out malformed or corrupted partial messages

        with self._lock:
            self.frames_received += 1
            # Unpack float parameters directly from match groups matching your data layout
            self.ch1_buffer.append(float(match.group(1)))
            self.ch2_buffer.append(float(match.group(2)))
            self.ch3_buffer.append(float(match.group(3)))
            self.ch4_buffer.append(float(match.group(4)))
            self._evaluate_buffer_saturation()

    def _generate_mock_frame(self):
        """Generates real-time synthetic wave data matrices for deterministic standalone checking."""
        t = time.time()
        v1 = np.sin(2 * np.pi * 45 * t) + np.random.normal(0, 0.2)
        v2 = np.sin(2 * np.pi * 0.5 * t) + np.random.normal(0, 0.05)
        v3 = np.sin(2 * np.pi * 0.2 * t) + np.random.normal(0, 0.05)
        v4 = np.sin(2 * np.pi * 7.83 * t) + np.random.normal(0, 0.3)

        with self._lock:
            self.frames_received += 1
            self.ch1_buffer.append(v1)
            self.ch2_buffer.append(v2)
            self.ch3_buffer.append(v3)
            self.ch4_buffer.append(v4)
            self._evaluate_buffer_saturation()

    def _evaluate_buffer_saturation(self):
        """Monitors spatial queues and executes asymmetric tensor compiling upon saturation."""
        if (
            len(self.ch1_buffer) >= 2560
            and len(self.ch4_buffer) >= 2560
            and len(self.ch2_buffer) >= 1280
        ):
            ch1_arr = np.array(self.ch1_buffer[-2560:], dtype=np.float32)
            ch2_arr = np.array(self.ch2_buffer[-1280:], dtype=np.float32)
            ch3_arr = np.array(self.ch3_buffer[-1280:], dtype=np.float32)
            ch4_arr = np.array(self.ch4_buffer[-2560:], dtype=np.float32)

            self.latest_tensor = self.pipeline.compile_feature_tensor(
                ch1_arr, ch2_arr, ch3_arr, ch4_arr
            )

            # Recaps arrays to minimize continuous RAM usage shifts over time
            self.ch1_buffer = self.ch1_buffer[-5120:]
            self.ch2_buffer = self.ch2_buffer[-2560:]
            self.ch3_buffer = self.ch3_buffer[-2560:]
            self.ch4_buffer = self.ch4_buffer[-5120:]

    def get_latest_ai_tensor(self) -> np.ndarray:
        """Thread-safe getter allowing external model loops to extract the processed (4, 1280) matrix."""
        with self._lock:
            return np.copy(self.latest_tensor)
