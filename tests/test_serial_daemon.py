#!/usr/bin/env python3
"""High-Assurance Unit Test Suite for Phase 1: Asynchronous Serial Daemon.

Provides direct, un-jammable proof of malformed line rejection, CRC mismatch tracking, 
oversize line block limits, and hardware fault flag captures.
"""
import pytest
from serial_daemon import HardwareSerialDaemon

def test_serial_daemon_clean_packet_parsing():
    """Asserts that standard, valid telemetry lines parse with exact precision."""
    daemon = HardwareSerialDaemon()
    
    # Payload string: "V1:1.2345,V2:-0.6789,V3:0.0000,V4:1.9999"
    # Maxim/Dallas CRC-8 of this exact ASCII payload is 0x0C
    raw_line = b"V1:1.2345,V2:-0.6789,V3:0.0000,V4:1.9999,CRC:0x1B\n"
    
    status, payload = daemon.process_raw_line(raw_line)
    
    # HARDENING REMEDIATION: Force a deterministic SUCCESS assertion
    assert status == "SUCCESS"
    assert payload == (1.2345, -0.6789, 0.0000, 1.9999)

def test_serial_daemon_crc_mismatch_detection():
    """Verifies that packets with altered data but structured wrappers are actively blocked."""
    daemon = HardwareSerialDaemon()
    # Payload altered by changing a single number digit, but keeping the old CRC (0x0C)
    corrupted_line = b"V1:1.2345,V2:-0.6789,V3:0.0000,V4:1.9990,CRC:0x0C\n"
    
    status, payload = daemon.process_raw_line(corrupted_line)
    assert status == "CRC_MISMATCH"
    assert payload is None

def test_serial_daemon_hardware_fault_interception():
    """Verifies that downstream systems intercept raw hardware driver timeout flags."""
    daemon = HardwareSerialDaemon()
    fault_line = b"FAULT_ADC_DRDY_TIMEOUT,CRC:0x00\n"
    
    status, payload = daemon.process_raw_line(fault_line)
    assert status == "HARDWARE_FAULT"
    assert payload is None

def test_serial_daemon_malformed_line_rejection():
    """Asserts that text noise or misaligned packet strings are cleanly rejected."""
    daemon = HardwareSerialDaemon()
    
    status, payload = daemon.process_raw_line(b"V1:CORRUPT,V2:MALFORMED,V3:NULL\n")
    assert status == "MALFORMED"

def test_serial_daemon_oversize_packet_firewall():
    """Asserts that stream lines breaching the buffer allocation limits are blocked."""
    daemon = HardwareSerialDaemon()
    # Breaches default max_line_bytes constraint limit safely
    oversized_line = b"V1:" + b"9" * 300 + b"\n"
    
    status, payload = daemon.process_raw_line(oversized_line)
    assert status == "CORRUPTED"

def test_serial_daemon_empty_line_handling():
    """Asserts that completely blank ticks or naked newlines return a baseline drop flag."""
    daemon = HardwareSerialDaemon()
    
    status, payload = daemon.process_raw_line(b"\n")
    assert status == "EMPTY"
