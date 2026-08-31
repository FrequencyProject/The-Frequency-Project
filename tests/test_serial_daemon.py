import time
import struct
from serial_daemon import HardwareSerialDaemon

def test_parser():
    d = HardwareSerialDaemon()
    v1, v2, v3, v4 = 1.0000, 2.0000, 3.0000, 4.0000
    
    payload_str = f"V1:{v1:.4f},V2:{v2:.4f},V3:{v3:.4f},V4:{v4:.4f}"
    expected_crc = d.compute_binary_crc8(payload_str.encode('utf-8'))
    
    test_line = f"{payload_str},CRC:0x{expected_crc:02X}".encode('utf-8')
    status, parsed_result = d.process_raw_line(test_line)
    
    assert status == "SUCCESS"
    assert parsed_result is not None
    assert abs(parsed_result[0] - v1) < 1e-4
    assert abs(parsed_result[1] - v2) < 1e-4

def test_hardware_fault_handling():
    d = HardwareSerialDaemon()
    fault_line = b"V1:FAULT,V2:FAULT,V3:FAULT,V4:FAULT\n"
    status, parsed_result = d.process_raw_line(fault_line)
    assert status == "HARDWARE_FAULT"
    assert parsed_result is None

def test_asynchronous_simulation_lifecycle():
    frames_captured = []
    
    def mock_session_callback(data_tuple):
        frames_captured.append(data_tuple)

    daemon = HardwareSerialDaemon(port="MOCK_BUS", callback=mock_session_callback, use_mock_fallback=True)
    daemon.start()
    time.sleep(0.1)
    daemon.stop()
    
    metrics = daemon.get_metrics()
    assert len(frames_captured) > 0
    assert metrics["frames_processed"] == len(frames_captured)
    assert metrics["frames_dropped"] == 0
    assert metrics["last_processing_latency_ms"] < 18.0

def test_firmware_to_daemon_parity():
    """Explicitly freezes the contract between the C++ firmware string and Python parser."""
    d = HardwareSerialDaemon()
    v1, v2, v3, v4 = -0.5123, 1.2048, 0.0000, -2.0480
    firmware_payload = f"V1:{v1:.4f},V2:{v2:.4f},V3:{v3:.4f},V4:{v4:.4f}"
    firmware_crc = d.compute_binary_crc8(firmware_payload.encode('utf-8'))
    serial_stream_line = f"{firmware_payload},CRC:0x{firmware_crc:02X}\n".encode('utf-8')
    
    status, result = d.process_raw_line(serial_stream_line)
    
    assert status == "SUCCESS"
    assert result == (v1, v2, v3, v4), "Protocol drift detected: Parser output deviated from the C++ format contract."
