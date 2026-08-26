#!/usr/bin/env python3
"""Unified Phase 2 Hardware Serial Ingestion Daemon.

Implements non-blocking physical serial port polling loops, automated linear 
reconnection backoff handling, and cryptographic telemetry signature dispatch.
"""
from typing import Optional, Callable, Tuple
import re
import threading
import time
import numpy as np
import serial  # Provided by the pinned pyserial dependency
from crypto_signer import HardwareTelemetrySigner


class HardwareSerialDaemon:
    """Manages background physical serial port life-cycles, data polling, and string parsing."""

    def __init__(self, port: str = "COM3", baudrate: int = 115200, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout

        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # Modified callback type hint to accept (payload_bytes, signature_bytes)
        self._callback: Optional[Callable[[Tuple[bytes, bytes]], None]] = None

        self.frames_received = 0
        self.frames_dropped = 0

        # Pre-compile regex at module level for high-throughput frame conversion speed
        self.packet_pattern = re.compile(
            r"^V1:([+-]?\d+\.?\d*),V2:([+-]?\d+\.?\d*),V3:([+-]?\d+\.?\d*),V4:([+-]?\d+\.?\d*)"
        )

        # Initialize the hardware-isolated cryptographic signer node
        self.signer = HardwareTelemetrySigner()

    def register_callback(self, callback: Callable[[Tuple[bytes, bytes]], None]) -> None:
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

        while self.is_running:
            ser = None
            try:
                # Bypass physical port acquisition entirely if running in an explicit mock/simulation environment
                if self.port.upper() in ["MOCK", "MOCK_TEST", "SIMULATION"]:
                    print(
                        f"[HW_DAEMON] Running in simulation sandbox loop. Simulating continuous hardware stream."
                    )
                    while self.is_running:
                        # Emulate an incoming hardware sensor packet clock pulse
                        mock_vector = np.random.normal(0.0, 1.0, 4).astype(np.float32)

                        # Cryptographically lock the telemetry array at the boundary using the TPM core
                        payload, signature = self.signer.sign_vector(mock_vector)

                        with self._lock:
                            if self._callback is not None:
                                self._callback((payload, signature))
                        time.sleep(0.1)
                    break

                # Attempt to claim the physical OS handle of the target copper bus port
                ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
                print(f"[HW_DAEMON] Successfully claimed copper line handle at {self.port}.")
                backoff = 1.0
                ser.reset_input_buffer()

                while self.is_running:
                    if not ser.is_open:
                        break

                    raw_bytes = ser.readline()
                    if not raw_bytes:
                        continue

                    try:
                        line_str = raw_bytes.decode("utf-8", errors="ignore")
                    except Exception:
                        continue

                    vector = self.parse_raw_line(line_str)
                    if vector is not None:
                        # Cryptographically lock the parsed float array via the TPM chip interface
                        payload, signature = self.signer.sign_vector(vector)

                        # Dispatch the verified payload tuple downstream to the adapter queues
                        with self._lock:
                            if self._callback is not None:
                                self._callback((payload, signature))

            except (serial.SerialException, OSError) as err:
                print(f"[HW_DAEMON WARNING] Physical connection lost or unavailable: {repr(err)}")
                print(
                    f"[HW_DAEMON] Initiating recovery tracking sequence. Retrying in {backoff}s..."
                )
                time.sleep(backoff)
                backoff = min(backoff + 2.0, 10.0)
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
    print("[INIT] Launching daemon sanity test pass...")
    daemon = HardwareSerialDaemon(port="MOCK_TEST")
    mock_line = "V1:1.23,V2:-4.56,V3:0.0,V4:7.89\n"
    parsed_vector = daemon.parse_raw_line(mock_line)
    print(f" -> Sanity Check Parsing Test Output: {parsed_vector}")
    assert parsed_vector is not None and len(parsed_vector) == 4

    # Verify signing operations output cleanly
    p, s = daemon.signer.sign_vector(parsed_vector)
    print(f" -> Sanity Check TPM Signature Output: {s.hex()[:16]}...")
    print("[SUCCESS] Core serial interface structures are optimized and verified.")
