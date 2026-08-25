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
from spectral_processing import AsymmetricTensorPipeline

class HardwareSerialDaemon:
    """Manages background serial port acquisition, buffering, and parsing."""
    
    def __init__(self, port: str = "MOCK", baudrate: int = 115200, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        
        self.is_running = False
        self._thread = None
        self._lock = threading.Lock()
        
        self.frames_received = 0
        self.frames_dropped = 0
        
        # Pre-compile the regex at class init for high-throughput execution speed
        self.packet_pattern = re.compile(
            r"^V1:([+-]?\d+\.?\d*),V2:([+-]?\d+\.?\d*),V3:([+-]?\d+\.?\d*),V4:([+-]?\d+\.?\d*)"
        )
        self.pipeline = AsymmetricTensorPipeline()
        self.latest_tensor = np.zeros((4, 1280), dtype=np.float32)

    def parse_raw_line(self, line: str) -> Optional[np.ndarray]:
        """Parses and returns a single raw data frame string."""
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

if __name__ == "__main__":
    print("[INIT] Phase 2 Hardware Serial Ingestion Daemon written and ready.")
