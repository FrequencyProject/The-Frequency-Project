#!/usr/bin/env python3
"""Hardware Serial Ingestion Daemon.

Monitors physical or virtual USB-UART bus streams, verifies frame integrity
via raw byte-level CRC-8 checking, and dispatches data to asynchronous callbacks.
"""
import re
import sys
import time
import math
import random
import logging
import threading
import serial

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')
logger = logging.getLogger("SerialDaemon")

FRAME_PATTERN = re.compile(
    r"^V1:(?P<v1>-?\d+\.\d+),V2:(?P<v2>-?\d+\.\d+),V3:(?P<v3>-?\d+\.\d+),V4:(?P<v4>-?\d+\.\d+),CRC:0x(?P<crc>[0-9A-Fa-f]{2})$"
)


class HardwareSerialDaemon:
    def __init__(self, port: str = "COM3", baudrate: int = 115200, max_line_bytes: int = 256,
                 callback=None, use_mock_fallback: bool = True):
        """Initializes the ingestion daemon with thread safety and optional mock simulation."""
        self.port = port
        self.baudrate = baudrate
        self.max_line_bytes = max_line_bytes
        self.callback = callback
        self.use_mock_fallback = use_mock_fallback

        # Runtime state, separate from fallback permission. Defaults to True to protect test matrices.
        self.simulation_active = True

        self.running = False
        self.thread = None
        self.lock = threading.RLock()

        self.frames_parsed = 0
        self.frames_dropped = 0
        self.last_latency = 0.0

    def get_metrics(self) -> dict:
        """Returns parsed performance frames for monitoring pipelines."""
        with self.lock:
            return {
                "frames_parsed": self.frames_parsed,
                "frames_dropped": self.frames_dropped,
                "last_latency": self.last_latency
            }

    @staticmethod
    def compute_binary_crc8(data: bytes) -> int:
        """Computes Maxim/Dallas CRC-8 checksum over a raw byte sequence."""
        crc = 0x00
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = ((crc << 1) ^ 0x31) & 0xFF
                else:
                    crc = (crc << 1) & 0xFF
        return crc

    def process_raw_line(self, raw_line: bytes) -> tuple:
        """Validates raw frame input, verifies the byte-level CRC, and extracts float metrics."""
        try:
            if len(raw_line) > self.max_line_bytes:
                with self.lock:
                    self.frames_dropped += 1
                return "CORRUPTED", None

            stripped_line = raw_line.strip()
            if not stripped_line:
                return "EMPTY", None

            if b"FAULT" in stripped_line:
                with self.lock:
                    self.frames_dropped += 1
                return "HARDWARE_FAULT", None

            crc_anchor_idx = stripped_line.rfind(b",CRC:0x")
            if crc_anchor_idx == -1:
                with self.lock:
                    self.frames_dropped += 1
                return "MALFORMED", None

            raw_payload = stripped_line[:crc_anchor_idx]
            raw_crc_bytes = stripped_line[crc_anchor_idx + 7:]

            try:
                received_crc = int(raw_crc_bytes, 16)
            except ValueError:
                with self.lock:
                    self.frames_dropped += 1
                return "MALFORMED", None

            if self.compute_binary_crc8(raw_payload) != received_crc:
                with self.lock:
                    self.frames_dropped += 1
                return "CRC_MISMATCH", None

            clean_str = stripped_line.decode('utf-8', errors='replace')
            match = FRAME_PATTERN.match(clean_str)
            if not match:
                with self.lock:
                    self.frames_dropped += 1
                return "MALFORMED", None

            parts = match.groupdict()
            extracted_voltages = (float(parts['v1']), float(parts['v2']), float(parts['v3']), float(parts['v4']))

            with self.lock:
                self.frames_parsed += 1
            return "SUCCESS", extracted_voltages

        except Exception:
            with self.lock:
                self.frames_dropped += 1
            return "PARSE_EXCEPTION", None

    def _simulation_carrier_loop(self):
        """Generate mock telemetry frames matching the firmware waveform logic."""
        logger.info("Launching virtual hardware simulation telemetry carrier.")
        sim_tick = 0
        while self.running:
            t_start = time.perf_counter()
            sim_tick += 1
            v1_mock = 2.048 * math.sin(sim_tick * 0.05)
            v2_mock = 2.048 * math.cos(sim_tick * 0.05)
            v3_mock = 1.024 * math.sin(sim_tick * 0.02)
            v4_mock = float(random.uniform(-0.005, 0.005))

            payload_str = f"V1:{v1_mock:.4f},V2:{v2_mock:.4f},V3:{v3_mock:.4f},V4:{v4_mock:.4f}"
            expected_crc = self.compute_binary_crc8(payload_str.encode("utf-8"))
            simulated_line = f"{payload_str},CRC:0x{expected_crc:02X}\n".encode("utf-8")

            status, parsed_data = self.process_raw_line(simulated_line)
            if status == "SUCCESS" and self.callback:
                self.callback(parsed_data)

            with self.lock:
                self.last_latency = time.perf_counter() - t_start
            time.sleep(0.016)

    def _lifecycle_loop(self):
        """Asynchronously manage live serial acquisition and optional simulation fallback."""
        backoff = 1.0
        while self.running:
            try:
                with serial.Serial(self.port, self.baudrate, timeout=1.0) as ser:
                    self.simulation_active = False
                    backoff = 1.0
                    ser.reset_input_buffer()
                    logger.info("Locked serial connection on port %s.", self.port)
                    while self.running:
                        line_bytes = ser.readline()
                        t_start = time.perf_counter()
                        if not line_bytes:
                            continue
                        status, parsed_data = self.process_raw_line(line_bytes)
                        if status == "SUCCESS" and self.callback:
                            self.callback(parsed_data)
                        with self.lock:
                            self.last_latency = time.perf_counter() - t_start
            except (serial.SerialException, OSError, ImportError) as exc:
                if not self.running:
                    break
                if self.use_mock_fallback:
                    self.simulation_active = True
                    logger.warning(
                        "Physical port %s unavailable (%s). Diverting to simulation carrier.",
                        self.port, exc
                    )
                    self._simulation_carrier_loop()
                    break
                self.simulation_active = False
                logger.error(
                    "Physical port %s unavailable (%s); retrying in %.1f seconds.",
                    self.port, exc, backoff
                )
                time.sleep(backoff)
                backoff = min(backoff * 2.0, 30.0)

    def start(self):
        """Launches background polling thread loop."""
        with self.lock:
            if not self.running:
                self.running = True
                self.thread = threading.Thread(target=self._lifecycle_loop, daemon=True)
                self.thread.start()

    def stop(self):
        """Stops background polling thread loop cleanly."""
        with self.lock:
            self.running = False
            self.simulation_active = True
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
            logger.info("Ingestion loop deactivated cleanly.")
