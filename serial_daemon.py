#!/usr/bin/env python3
"""Phase 2: High-Speed Serial Ingestion Daemon.

Monitors physical USB-UART bus streams, insulates the pipeline against 
environmental line noise corruption, and parses raw waveform telemetry frames.
"""
import re
import sys
import logging
import numpy as np

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')
logger = logging.getLogger("SerialDaemon")

class VivicSerialDaemon:
    def __init__(self, port: str = "COM3", baud: int = 115200, max_line_bytes: int = 256):
        """Initializes the ingestion daemon with explicit sanity-bounding gates."""
        self.port = port
        self.baud = baud
        self.max_line_bytes = max_line_bytes  # Hard boundary protection against memory floods
        
        # Telemetry structural health counters
        self.frames_parsed = 0
        self.frames_dropped = 0
        
        # Strict validation pattern matching our exact firmware footprint
        self.telemetry_regex = re.compile(
            r"^V1:([+-]?\d+\.?\d*|FAULT),V2:([+-]?\d+\.?\d*|FAULT),V3:([+-]?\d+\.?\d*|FAULT),V4:([+-]?\d+\.?\d*|FAULT)$"
        )

    def process_raw_line(self, raw_line: bytes) -> tuple:
        """Sanitizes, validates, and decodes incoming serial string packets."""
        try:
            # 1. Enforce strict upper physical size constraints to block buffer overruns
            if len(raw_line) > self.max_line_bytes:
                self.frames_dropped += 1
                logger.warning(f"Line bounds breached ({len(raw_line)} bytes). Purging corrupted frame.")
                return "CORRUPTED", None

            # 2. Decode string characters safely passing through replacement fallback nodes
            clean_str = raw_line.decode('utf-8', errors='replace').strip()
            if not clean_str:
                return "EMPTY", None

            # 3. Check for the bare-metal hardware timeout sentinel alert first
            if "FAULT" in clean_str:
                self.frames_dropped += 1
                logger.error("[💥 HARDWARE ALERT] Embedded firmware reporting an active ADC DRDY pin timeout!")
                return "HARDWARE_FAULT", None

            # 4. Evaluate stream fields against structural regular expressions
            match = self.telemetry_regex.match(clean_str)
            if not match:
                self.frames_dropped += 1
                logger.warning(f"Regex match failure on line: '{clean_str}'. Dropping malformed frame.")
                return "MALFORMED", None

            # 5. Safely convert parsed capture groups into highly optimized numpy arrays
            extracted_voltages = np.array([float(x) for x in match.groups()], dtype=np.float32)
            self.frames_parsed += 1
            return "SUCCESS", extracted_voltages

        except Exception as err:
            self.frames_dropped += 1
            logger.error(f"Unexpected parsing exception intercepted in ingestion loop: {str(err)}")
            return "PARSE_EXCEPTION", None

if __name__ == "__main__":
    print("[TEST] Launching serial daemon ingestion robustness validation pass...")
    daemon = VivicSerialDaemon()
    
    # Generate test beds simulating various line data scenarios
    good_frame = b"V1:0.1234,V2:-1.0500,V3:2.0480,V4:0.0012\n"
    fault_frame = b"V1:FAULT,V2:FAULT,V3:FAULT,V4:FAULT\n"
    corrupted_noise = b"V1:0.1234,V2:,V3:2.0480,V4:0.0012\n" # Electrostatic injection simulation
    flooded_buffer = b"V" * 300 # Memory exhaustion attack vectors simulation
    
    # Process test arrays through the defensive validation layers
    s1, d1 = daemon.process_raw_line(good_frame)
    s2, d2 = daemon.process_raw_line(fault_frame)
    s3, d3 = daemon.process_raw_line(corrupted_noise)
    s4, d4 = daemon.process_raw_line(flooded_buffer)
    
    assert s1 == "SUCCESS" and d1 is not None, "Valid telemetry stream formats must pass through smoothly."
    assert s2 == "HARDWARE_FAULT", "Firmware alert flags must be caught instantly."
    assert s3 == "MALFORMED", "Noise anomalies must be intercepted cleanly without a script crash."
    assert s4 == "CORRUPTED", "Memory floods must trip upper line size limit filters."
    
    print(f"[SUCCESS] Ingestion loop test complete. Parsed: {daemon.frames_parsed}, Dropped: {daemon.frames_dropped}")
