import struct
import numpy as np
from serial_daemon import VivicSerialDaemon, HardwareSerialDaemon

def test_parser():
    d = VivicSerialDaemon()
    v1, v2, v3, v4 = 1.0000, 2.0000, 3.0000, 4.0000
    
    payload_str = f"V1:{v1:.4f},V2:{v2:.4f},V3:{v3:.4f},V4:{v4:.4f}"
    expected_crc = d.compute_binary_crc8(payload_str.encode('utf-8'))
    
    test_line = f"{payload_str},CRC:0x{expected_crc:02X}".encode('utf-8')
    status, parsed_result = d.process_raw_line(test_line)
    
    assert status == "SUCCESS"
    assert parsed_result is not None
    assert np.allclose(parsed_result, [v1, v2, v3, v4])

def test_hardware_fault_handling():
    d = VivicSerialDaemon()
    fault_line = b"V1:FAULT,V2:FAULT,V3:FAULT,V4:FAULT\n"
    status, parsed_result = d.process_raw_line(fault_line)
    assert status == "HARDWARE_FAULT"
    assert parsed_result is None

def test_asynchronous_simulation_lifecycle():
    frames_captured = []
    
    def mock_session_callback(tensor):
        frames_captured.append(tensor)

    daemon = VivicSerialDaemon(port="/dev/null", callback=mock_session_callback, use_mock_fallback=True)
    daemon.start()
    import time
    time.sleep(0.1)
    daemon.stop()
    metrics = daemon.get_metrics()
    
    assert len(frames_captured) > 0
    assert metrics["frames_processed"] == len(frames_captured)
    assert metrics["frames_dropped"] == 0
    assert metrics["last_processing_latency_ms"] < 18.0

def test_backward_compatibility_alias():
    # Verify that old-style callers still initialize perfectly through the wrapper alias
    d = HardwareSerialDaemon()
    assert isinstance(d, VivicSerialDaemon)
