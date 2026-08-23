#!/usr/bin/env python3
"""Unified Phase 2 Hardware Serial Ingestion Daemon.

Combines strict regex validation with non-blocking threading,
automatic port reconnection, and decoupled thread-safe window processing.
"""
from typing import Optional
import re
import threading
import time
import numpy as np
import serial
from spectral_processing import AsymmetricTensorPipeline

class ResilientSerialDaemon:
    """Manages background serial port acquisition with decoupled concurrency processing."""

    def __init__(self, port: str = "MOCK", baudrate: int = 115200, timeout: float = 1.0, packet_callback=None):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.packet_callback = packet_callback

        self.is_running = False
        self._thread = None
        self._lock = threading.Lock()

        self.frames_received = 0
        self.frames_dropped = 0

        self.ch1_buffer: list[float] = []
        self.ch2_buffer: list[float] = []
        self.ch3_buffer: list[float] = []
        self.ch4_buffer: list[float] = []

        self.packet_pattern = re.compile(
            r"^V1:([+-]?\d+\.?\d*),V2:([+-]?\d+\.?\d*),V3:([+-]?\d+\.?\d*),V4:([+-]?\d+\.?\d*)"
        )

        self.pipeline = AsymmetricTensorPipeline()
        self.latest_tensor = np.zeros((4, 1280), dtype=np.float32)

    def parse_raw_line(self, line: str) -> Optional[np.ndarray]:
        """Backward-compatible helper to parse and return a single packet frame."""
        clean_str = line.strip()
        if not clean_str:
            return None
        match = self.packet_pattern.match(clean_str)
        if not match:
            with self._lock:
                self.frames_dropped += 1
            return None
        with self._lock:
            self.frames_received += 1
        return np.array([float(x) for x in match.groups()], dtype=np.float32)

    def ingest_packet_string(self, packet_str: str) -> bool:
        """Public ingestion interface that decouples heavy CPU math from thread locks."""
        clean_str = packet_str.strip()
        match = self.packet_pattern.match(clean_str)
        if not match:
            with self._lock:
                self.frames_dropped += 1
            return False

        v1, v2, v3, v4 = (float(x) for x in match.groups())
        data_to_compute = None

        with self._lock:
            self.frames_received += 1
            self.ch1_buffer.append(v1)
            self.ch2_buffer.append(v2)
            self.ch3_buffer.append(v3)
            self.ch4_buffer.append(v4)

            if (len(self.ch1_buffer) >= 2560 and len(self.ch4_buffer) >= 2560 and 
                len(self.ch2_buffer) >= 1280 and len(self.ch3_buffer) >= 1280):

                data_to_compute = (
                    np.array(self.ch1_buffer[-2560:], dtype=np.float32),
                    np.array(self.ch2_buffer[-1280:], dtype=np.float32),
                    np.array(self.ch3_buffer[-1280:], dtype=np.float32),
                    np.array(self.ch4_buffer[-2560:], dtype=np.float32)
                )
                self.ch1_buffer = self.ch1_buffer[-5120:]
                self.ch2_buffer = self.ch2_buffer[-2560:]
                self.ch3_buffer = self.ch3_buffer[-2560:]
                self.ch4_buffer = self.ch4_buffer[-5120:]

        if data_to_compute is not None:
            compiled = self.pipeline.compile_feature_tensor(*data_to_compute)
            with self._lock:
                self.latest_tensor = compiled
            if self.packet_callback:
                self.packet_callback(compiled)

        return True

    def start(self):
        """Starts the non-blocking background polling worker loop."""
        with self._lock:
            if self.is_running:
                return
            self.is_running = True
            self._thread = threading.Thread(target=self._worker_loop, daemon=True)
            self._thread.start()

    def stop(self):
        """Stops the background worker and releases port resources."""
        with self._lock:
            self.is_running = False
        if self._thread:
            self._thread.join(timeout=2.0)

    def _worker_loop(self):
        ser = None
        while self.is_running:
            if self.port.upper() == "MOCK":
                self._generate_mock_frame()
                time.sleep(0.001)
                continue

            if ser is None or not ser.is_open:
                try:
                    ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
                    ser.reset_input_buffer()
                except Exception:
                    time.sleep(3.0)
                    continue

            try:
                if ser.in_waiting > 0:
                    raw_line = ser.readline()
                    decoded_line = raw_line.decode("utf-8", errors="ignore").strip()
                    if decoded_line:
                        self.ingest_packet_string(decoded_line)
            except Exception:
                if ser:
                    try: ser.close()
                    except Exception: pass
                ser = None
                time.sleep(1.0)

    def _generate_mock_frame(self):
        t = time.time()
        v1 = np.sin(2 * np.pi * 45 * t) + np.random.normal(0, 0.2)
        v2 = np.sin(2 * np.pi * 0.5 * t) + np.random.normal(0, 0.05)
        v3 = np.sin(2 * np.pi * 0.2 * t) + np.random.normal(0, 0.05)
        v4 = np.sin(2 * np.pi * 7.83 * t) + np.random.normal(0, 0.3)
        self.ingest_packet_string(f"V1:{v1:.4f},V2:{v2:.4f},V3:{v3:.4f},V4:{v4:.4f}")

    def get_latest_ai_tensor(self) -> np.ndarray:
        """Thread-safe getter mapping the current (4, 1280) feature tensor."""
        with self._lock:
            return np.copy(self.latest_tensor)

# Explicit backward-compatibility shim
HardwareSerialDaemon = ResilientSerialDaemon
