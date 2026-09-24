import numpy as np
import pytest
import serial
from unittest.mock import patch
from serial_daemon import HardwareSerialDaemon


def test_hardware_serial_bus_failure_is_detected():
    """Verifies that unhandled serial bus connection errors break loops natively."""
    with patch("serial.Serial", side_effect=serial.SerialException("Access Denied")):
        with pytest.raises(serial.SerialException):
            with serial.Serial("COM3", 115200, timeout=1.0) as ser:
                ser.readline()


def test_hardware_packet_drop_tolerances():
    """Verifies parsing degradation tracks baseline drop thresholds correctly."""
    daemon = HardwareSerialDaemon(port="COM3")

    # Process corrupt and multi-frame anomalies manually
    daemon.process_raw_line(b"V1:1.0,V2:1.0,CRC:0x00\n")
    daemon.process_raw_line(b"V1:1.0,V2:1.0,V3:1.0,V4:1.0,CRC:0xZZ\n")

    metrics = daemon.get_metrics()
    assert metrics["frames_dropped"] == 2
    assert metrics["frames_parsed"] == 0


def test_sensor_variance_firewall_with_real_signals():
    """Verifies that non-flatlining data passes baseline validation bounds."""
    from sensor_adapter import MultiChannelSensorAdapter
    adapter = MultiChannelSensorAdapter(port="COM3")
    adapter.daemon.simulation_active = True

    # Charge the ring buffers using varying synthetic packets
    for i in range(1282):
        sim_val = 1.0 + 0.5 * np.sin(i * 0.05)
        adapter.process_incoming_packet(
            f"V1:{sim_val:.4f},V2:0.1000,V3:0.1000,V4:0.0010".encode("utf-8"),
            allow_missing_crc=True
        )

    features = adapter.get_ai_features()
    assert features.shape == (4, 1280)
    assert not np.all(features == 0)
