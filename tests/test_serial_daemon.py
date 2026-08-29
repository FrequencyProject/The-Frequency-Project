import struct
import numpy as np
from serial_daemon import HardwareSerialDaemon

def test_parser():
    # Instantiate the daemon (using placeholder port string for testing initialization)
    d = HardwareSerialDaemon(port="/dev/ttyUSB0")
    
    # 1. Define the exact float values we expect to test
    v1, v2, v3, v4 = 1.0, 2.0, 3.0, 4.0
    
    # 2. Pack them into standard 16-byte C-struct binary layout (Little-Endian '<ffff')
    binary_data = struct.pack("<ffff", v1, v2, v3, v4)
    
    # 3. Calculate the expected Dallas/Maxim CRC-8 checksum
    expected_crc = d.compute_binary_crc8(binary_data)
    
    # 4. Construct the precise string that the firmware would broadcast
    test_line = f"V1:{v1:.4f},V2:{v2:.4f},V3:{v3:.4f},V4:{v4:.4f},CRC:0x{expected_crc:02X}"
    
    # 5. Execute parsing and verify it passes instead of returning None
    parsed_result = d.parse_and_verify(test_line)
    
    assert parsed_result is not None
    assert parsed_result["v1"] == v1
    assert parsed_result["v2"] == v2
    assert parsed_result["v3"] == v3
    assert parsed_result["v4"] == v4

def test_hardware_fault_handling():
    d = HardwareSerialDaemon(port="/dev/ttyUSB0")
    # Verify that a hardware fault sentinel returns None gracefully instead of crashing
    fault_line = "V1:FAULT,V2:FAULT,V3:FAULT,V4:FAULT"
    assert d.parse_and_verify(fault_line) is None
