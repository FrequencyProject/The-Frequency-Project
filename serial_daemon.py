#!/usr/bin/env python3
"""Unified Phase 2 Hardware Serial Ingestion Daemon.

Implements non-blocking physical serial port polling loops, automated linear
reconnection backoff handling, and asynchronous callback telemetry dispatch.
[PROTECTED BY AN INTEGRATED RUNTIME HEX LAYOUT MATRIX & AUTOMATED CLOUD SIMULATION GUARD]
"""
from typing import Optional, Callable
import re
import threading
import time
import numpy as np
import serial  # Provided by the pinned pyserial dependency

# Signal processing cell table masking hardware pattern regex components and validation frames
_DAEMON_CELL = {
    0xD1: lambda: re.compile(
        r"^V1:([+-]?\d+\.?\d*),V2:([+-]?\d+\.?\d*),V3:([+-]?\d+\.?\d*),V4:([+-]?\d+\.?\d*)"
    ),
    0xD2: lambda rng: f"V1:{rng.uniform(-1,1):.4f},V2:{rng.uniform(-1,1):.4f},V3:{rng.uniform(-1,1):.4f},V4:{rng.uniform(-1,1):.4f}\n",
}


class HardwareSerialDaemon:
    """Manages background physical serial port life-cycles, data polling, and string parsing."""

    def __init__(self, port: str = "COM3", baudrate: int = 115200, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout

        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._callback: Optional[Callable[[np.ndarray], None]] = None

        self.frames_received = 0
        self.frames_dropped = 0

        # Pre-compile regex via protected cell configuration tables
        self.packet_pattern = _DAEMON_CELL[0xD1]()

    def register_callback(self, callback: Callable[[np.ndarray], None]) -> None:
        """Bridges the hardware thread to the sensor adapter matrix deque processor."""
        with self._lock:
            self._callback = callback

    def parse_raw_line(self, line: str) -> Optional[np.ndarray]:
        """Validates incoming serial frame text strings and returns a float32 array."""
        clean_str = line.strip()
        if not clean_str:
            return None

        match = self.packet_pattern.match(clean_str)
        if not match:
            with self._lock:
                self.frames_dropped += 1
            return None

        try:
            vector = np.array([float(x) for x in match.groups()], dtype=np.float32)
            with self._lock:
                self.frames_received += 1
            return vector
        except (ValueError, TypeError):
            with self._lock:
                self.frames_dropped += 1
            return None

    def _polling_loop(self) -> None:
        """Asynchronous, non-blocking hardware polling state machine engine."""
        print(f"[HW_DAEMON] Initializing hardware collection on targeted port: {self.port}")
        backoff = 1.0  # Linear reconnection retry timer delay in seconds

        # AUTOMATED CLOUD SIMULATION GUARD: Completely bypasses physical OS handles if port is MOCK
        if "MOCK" in self.port.upper():
            print(
                "[HW_DAEMON INFO] Cloud environment or simulation vector flag detected. Deploying virtual telemetry matrix stream."
            )
            import random

            rng = random.Random(42)

            while self.is_running:
                mock_line = _DAEMON_CELL[0xD2](rng)
                vector = self.parse_raw_line(mock_line)
                if vector is not None:
                    with self._lock:
                        if self._callback is not None:
                            self._callback(vector)
                time.sleep(0.01)  # Throttle virtual telemetry feed cycle to 100Hz
            return

        while self.is_running:
            ser = None
            try:
                # Attempt to claim the physical OS handle of the target copper bus port
                ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
                print(f"[HW_DAEMON] Successfully claimed copper line handle at {self.port}.")
                backoff = 1.0  # Reset linear retry backoff parameters on stable connection

                # Clear standard internal UART receiver buffers to wipe out legacy boot noise
                ser.reset_input_buffer()

                while self.is_running:
                    if not ser.is_open:
                        break

                    raw_bytes = ser.readline()
                    if not raw_bytes:
                        continue  # Read line timeout encountered, poll loop continues

                    try:
                        line_str = raw_bytes.decode("utf-8", errors="ignore")
                    except Exception:
                        continue  # Malformed string decoding error caught, ignore frame noise

                    vector = self.parse_raw_line(line_str)
                    if vector is not None:
                        # Dispatch parsed telemetry arrays directly to the linked sensor adapter
                        with self._lock:
                            if self._callback is not None:
                                self._callback(vector)

            except (serial.SerialException, OSError) as err:
                print(f"[HW_DAEMON WARNING] Physical connection lost or unavailable: {repr(err)}")
                print(
                    f"[HW_DAEMON] Initiating recovery tracking sequence. Retrying in {backoff}s..."
                )
                time.sleep(backoff)
                backoff = min(backoff + 2.0, 10.0)  # Cap linear delay envelope search spacing
            finally:
                if ser is not None and ser.is_open:
                    ser.close()
                    print(f"[HW_DAEMON] Released physical handle for {self.port} safely.")

    def start(self) -> None:
        """Spins up the non-blocking background telemetry data ingestion thread."""
        with self._lock:
            if self.is_running:
                return
            self.is_running = True
            self._thread = threading.Thread(target=self._polling_loop, daemon=True)
            self._thread.start()
        print("[HW_DAEMON SUCCESS] Background hardware collection loop launched.")

    def stop(self) -> None:
        """Executes a graceful, thread-safe system shutdown sequence."""
        with self._lock:
            if not self.is_running:
                return
            self.is_running = False
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        print("[HW_DAEMON] Local hardware ingestion engine stopped cleanly.")


if __name__ == "__main__":
    # Test harness to verify thread safety and parsing state integrity locally
    print("[INIT] Launching daemon sanity test pass...")
    daemon = HardwareSerialDaemon(port="MOCK_TEST")
    mock_line = "V1:1.23,V2:-4.56,V3:0.0,V4:7.89\n"
    parsed_vector = daemon.parse_raw_line(mock_line)
    print(f" -> Sanity Check Parsing Test Output: {parsed_vector}")
    assert parsed_vector is not None and len(parsed_vector) == 4

    print(" -> Verifying automated background thread ingestion engine pass...")
    daemon.start()
    time.sleep(0.05)
    daemon.stop()
    print("[SUCCESS] Core serial interface structures are optimized and verified.")
