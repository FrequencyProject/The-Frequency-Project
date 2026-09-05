#!/usr/bin/env python3
"""Hardware Serial Ingestion Daemon.

Monitors physical or virtual USB-UART bus streams, verifies frame integrity
via raw byte-level CRC-8 checking, and dispatches data to asynchronous callbacks.
"""
import re
import sys
import time
import random
import logging
import threading
import serial

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')
logger = logging.getLogger("SerialDaemon")

# Configuration regex for matching incoming telemetry frames
FRAME_PATTERN = re.compile(
    r"^V1:(?P<v1>-?\d+\.\d{4}),V2:(?P<v2>-?\d+\.\d{4}),V3:(?P<v3>-?\d+\.\d{4}),V4:(?P<v4>-?\d+\.\d{4}),CRC:0x(?P<crc>[0-9A-Fa-f]{2})$"
)

class HardwareSerialDaemon:
    def __init__(self, port: str = "COM3", baudrate: int = 115200, max_line_bytes: int = 256, callback=None, use_mock_fallback: bool = True):
        """Initializes the ingestion daemon with thread safety and optional mock simulation."""
        self.port = port
        self.baudrate = baudrate
        self.max_line_bytes = max_line_bytes
        self.callback = callback
        self.use_mock_fallback = use_mock_fallback

        self.running = False
        self.thread = None
        self.lock = threading.RLock()

        # Telemetry metrics counters
        self.frames_parsed = 0
        self.frames_dropped = 0
        self.last_latency = 0.0

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
                logger.warning(f"Line limit exceeded ({len(raw_line)} bytes). Purging frame.")
                return "CORRUPTED", None

            # 1. HARDENING REMEDIATION: Direct Byte-Surgical Substring Isolation.
            # Strips and checks raw byte anchors to eliminate redundant intermediate 
            # re-encoding string operations from the 60Hz processing hot path.
            stripped_line = raw_line.strip()
            if not stripped_line:
                return "EMPTY", None

            if b"FAULT" in stripped_line:
                with self.lock:
                    self.frames_dropped += 1
                logger.error("Firmware reported an active hardware ADC DRDY pin timeout.")
                return "HARDWARE_FAULT", None

            # Verify presence of the trailing CRC anchor signature natively on bytes
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

            # Validate transmission integrity via native raw byte checksumming
            if self.compute_binary_crc8(raw_payload) != received_crc:
                with self.lock:
                    self.frames_dropped += 1
                logger.warning("Byte-level CRC verification mismatch. Dropping frame.")
                return "CRC_MISMATCH", None

            # 2. Decode string only after data integrity is verified completely
            clean_str = stripped_line.decode('utf-8', errors='replace')
            match = FRAME_PATTERN.match(clean_str)
            if not match:
                with self.lock:
                    self.frames_dropped += 1
                logger.warning(f"Regex parsing failure on line: '{clean_str}'")
                return "MALFORMED", None

            parts = match.groupdict()
            extracted_voltages = (float(parts['v1']), float(parts['v2']), float(parts['v3']), float(parts['v4']))

            with self.lock:
                self.frames_parsed += 1
            return "SUCCESS", extracted_voltages

        except Exception as err:
            with self.lock:
                self.frames_dropped += 1
            logger.error(f"Unexpected parsing exception encountered: {str(err)}")
            return "PARSE_EXCEPTION", None

    def _simulation_carrier_loop(self):
        """Generates mock telemetry frames when physical hardware is absent."""
        logger.info("Launching virtual hardware simulation telemetry carrier.")
        rng = random.Random()

        while self.running:
            t_start = time.perf_counter()

            payload_str = f"V1:{rng.uniform(-1,1):.4f},V2:{rng.uniform(-1,1):.4f},V3:{rng.uniform(-1,1):.4f},V4:{rng.uniform(-1,1):.4f}"
            expected_crc = self.compute_binary_crc8(payload_str.encode('utf-8'))
            simulated_line = f"{payload_str},CRC:0x{expected_crc:02X}\n".encode('utf-8')

            status, parsed_data = self.process_raw_line(simulated_line)
            if status == "SUCCESS" and self.callback:
                self.callback(parsed_data)

            # Consolidated lock updates to prevent instruction-level thread thrashing
            with self.lock:
                self.last_latency = time.perf_counter() - t_start
            time.sleep(0.016)  # 60Hz timing constraint loop

    def _lifecycle_loop(self):
        """Asynchronous execution loop handling connection management."""
        backoff = 1.0
        while self.running:
            try:
                with serial.Serial(self.port, self.baudrate, timeout=1.0) as ser:
                    backoff = 1.0
                    ser.reset_input_buffer()
                    logger.info(f"Locked serial connection on port {self.port}.")

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

            except (serial.SerialException, OSError, ImportError):
                if not self.running:
                    break
                if self.use_mock_fallback:
                    logger.warning(f"Physical port {self.port} unavailable. Diverting to simulation carrier...")
                    self._simulation_carrier_loop()
                    break
                else:
                    time.sleep(backoff)
                    backoff = min(backoff * 2.0, 30.0)

    def start(self):
        """Launches background polling thread loop."""
        with self.lock:
            if not self.running:
                self.running = True
                self.thread = threading.Thread(target=self._lifecycle_loop, daemon=True)
                self.thread.start()
                logger.info(f"Ingestion loop activated on port {self.port}.")

    def stop(self):
        """Stops background polling thread loop cleanly."""
        with self.lock:
            self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
            logger.info("Ingestion loop deactivated cleanly.")

    def get_metrics(self) -> dict:
        """Returns thread-isolated performance counters."""
        with self.lock:
            return {
                "frames_processed": self.frames_parsed,
                "frames_dropped": self.frames_dropped,
                "last_processing_latency_ms": self.last_latency * 1000.0
            }

# BACKWARD COMPATIBILITY ALIAS ASSIGNMENT
VivicSerialDaemon = HardwareSerialDaemon
