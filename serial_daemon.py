import sys
import time
import re
import struct
import threading
import serial

class HardwareSerialDaemon:
    def __init__(self, port: str, baudrate: int = 115200, callback=None):
        self.port = port
        self.baudrate = baudrate
        self.callback = callback
        self.running = False
        self.thread = None
        self.lock = threading.RLock()
        
        # Statistics metrics tracking
        self.frame_count = 0
        self.dropped_frames = 0
        self.last_latency = 0.0

        # String matching framework including the trailing hexadecimal CRC segment
        self.frame_regex = re.compile(
            r"^V1:(?P<v1>-?\d+\.\d+),V2:(?P<v2>-?\d+\.\d+),V3:(?P<v3>-?\d+\.\d+),V4:(?P<v4>-?\d+\.\d+),CRC:0x(?P<crc>[0-9A-Fa-f]{2})$"
        )

    @staticmethod
    def compute_binary_crc8(data: bytes) -> int:
        """Computes matching Dallas/Maxim CRC-8 checksum over raw byte sequences."""
        crc = 0x00
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = ((crc << 1) ^ 0x31) & 0xFF
                else:
                    crc = (crc << 1) & 0xFF
        return crc

    def parse_and_verify(self, line: str) -> dict | None:
        """Parses line, packs floats to binary format, and validates byte parity."""
        cleaned = line.strip()
        
        # Capture hardware fault strings directly
        if "FAULT" in cleaned:
            with self.lock:
                self.dropped_frames += 1
            return None

        match = self.frame_regex.match(cleaned)
        if not match:
            with self.lock:
                self.dropped_frames += 1
            return None

        parts = match.groupdict()
        try:
            v1 = float(parts['v1'])
            v2 = float(parts['v2'])
            v3 = float(parts['v3'])
            v4 = float(parts['v4'])
            received_crc = int(parts['crc'], 16)
            
            # Pack into standard IEEE-754 binary representation (Little-Endian float tuple)
            binary_payload = struct.pack("<ffff", v1, v2, v3, v4)
        except (ValueError, struct.error, OverflowError):
            with self.lock:
                self.dropped_frames += 1
            return None

        # Confirm parity signature checks match perfectly
        if self.compute_binary_crc8(binary_payload) != received_crc:
            with self.lock:
                self.dropped_frames += 1
            return None

        with self.lock:
            self.frame_count += 1
            
        return {"v1": v1, "v2": v2, "v3": v3, "v4": v4}

    def _lifecycle_loop(self):
        backoff = 1.0
        while self.running:
            try:
                with serial.Serial(self.port, self.baudrate, timeout=1.0) as ser:
                    backoff = 1.0  # Reset backoff on successful hook
                    ser.reset_input_buffer()
                    
                    while self.running:
                        line_bytes = ser.readline()
                        t_start = time.perf_counter()
                        
                        if not line_bytes:
                            continue
                            
                        try:
                            decoded_line = line_bytes.decode('utf-8', errors='ignore')
                        except Exception:
                            with self.lock:
                                self.dropped_frames += 1
                            continue

                        parsed_data = self.parse_and_verify(decoded_line)
                        if parsed_data and self.callback:
                            self.callback(parsed_data)
                            
                        with self.lock:
                            self.last_latency = time.perf_counter() - t_start

            except (serial.SerialException, OSError):
                if not self.running:
                    break
                time.sleep(backoff)
                backoff = min(backoff * 2.0, 30.0) # Exponential ceiling bounds

    def start(self):
        with self.lock:
            if not self.running:
                self.running = True
                self.thread = threading.Thread(target=self._lifecycle_loop, daemon=True)
                self.thread.start()

    def stop(self):
        with self.lock:
            self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)

    def get_metrics(self) -> dict:
        with self.lock:
            return {
                "frames_processed": self.frame_count,
                "frames_dropped": self.dropped_frames,
                "last_processing_latency_ms": self.last_latency * 1000.0
            }
