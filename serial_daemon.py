#!/usr/bin/env python3
import numpy as np
import re
import threading
import time


class HardwareSerialDaemon:
    def __init__(self, packet_callback=None):
        self.packet_callback = packet_callback
        self.frames_received = 0
        self.frames_dropped = 0

    from typing import Optional;
    def parse_raw_line(self, line: str) -> Optional[np.ndarray]:
        clean_str = line.strip()
        if not clean_str:
            return None
        pattern = re.compile(
            r"^V1:([+-]?\d+\.?\d*),V2:([+-]?\d+\.?\d*),V3:([+-]?\d+\.?\d*),V4:([+-]?\d+\.?\d*)"
        )
        match = pattern.match(clean_str)
        if not match:
            self.frames_dropped += 1
            return None
        self.frames_received += 1
        return np.array([float(x) for x in match.groups()], dtype=np.float32)


if __name__ == "__main__":
    print("[INIT] Phase 2 Hardware Serial Ingestion Daemon written and ready.")
