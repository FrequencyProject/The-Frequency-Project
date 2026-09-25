import unittest.mock as mock
import serial
from sensor_adapter import SensorAdapter
from serial_daemon import HardwareSerialDaemon


def test_live_mode_drops_saturated_frame():
    adapter = SensorAdapter(port="TEST")
    adapter.daemon.simulation_active = False
    adapter._packet_ingestion_callback((2.0480, 0.1, 0.1, 0.1))
    assert adapter.frames_dropped == 1
    assert adapter.frames_received == 0


def test_live_mode_drops_non_numeric_frame():
    adapter = SensorAdapter(port="TEST")
    adapter.daemon.simulation_active = False
    adapter._packet_ingestion_callback(("invalid", 0.1, 0.1, 0.1))
    assert adapter.frames_dropped == 1
    assert adapter.frames_received == 0


def test_simulation_mode_allows_synthetic_boundary_value():
    adapter = SensorAdapter(port="TEST")
    adapter.daemon.simulation_active = True
    adapter._packet_ingestion_callback((2.0480, 0.1, 0.1, 0.1))
    assert adapter.frames_dropped == 0
    assert adapter.frames_received == 1


def test_fallback_marks_simulation_active(monkeypatch):
    daemon = HardwareSerialDaemon(use_mock_fallback=True)
    daemon.running = True
    observed = {}

    def fake_serial(*args, **kwargs):
        raise serial.SerialException("Serial port unavailable")

    def fake_simulation_loop():
        observed["simulation_active"] = daemon.simulation_active
        daemon.running = False

    monkeypatch.setattr("serial_daemon.serial.Serial", fake_serial)
    monkeypatch.setattr(daemon, "_simulation_carrier_loop", fake_simulation_loop)

    daemon._lifecycle_loop()

    assert observed["simulation_active"] is True
    assert daemon.simulation_active is True


def test_successful_serial_lock_resets_simulation_active(monkeypatch):
    daemon = HardwareSerialDaemon(use_mock_fallback=True)
    daemon.running = True
    daemon.simulation_active = True

    mock_ser = mock.MagicMock()
    mock_ser.readline.side_effect = [b"V1:1.0,V2:1.0,V3:1.0,V4:1.0,CRC:0xAA\n"]

    def fake_serial(*args, **kwargs):
        return mock_ser

    original_process = daemon.process_raw_line

    def wrap_process(*args, **kwargs):
        res = original_process(*args, **kwargs)
        daemon.running = False
        return res

    monkeypatch.setattr("serial_daemon.serial.Serial", fake_serial)
    monkeypatch.setattr(daemon, "process_raw_line", wrap_process)

    daemon._lifecycle_loop()
    assert daemon.simulation_active is False
