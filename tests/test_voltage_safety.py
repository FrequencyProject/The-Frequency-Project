import unittest.mock as mock
import serial
from sensor_adapter import SensorAdapter
from serial_daemon import HardwareSerialDaemon


# =====================================================================
# 1. HARDWARE BOUNDARY SAFETY CHECKS (Clipping & Input Firewalls)
# =====================================================================

def test_hardware_boundary_drops_saturated_voltage_frame():
    """Verify live hardware mode immediately drops frames at or above 2.0480V."""
    adapter = SensorAdapter(port="TEST")
    adapter.daemon.simulation_active = False

    adapter._packet_ingestion_callback((2.0480, 0.1, 0.1, 0.1))

    assert adapter.frames_dropped == 1
    assert adapter.frames_received == 0


def test_hardware_boundary_drops_non_numeric_telemetry_frame():
    """Verify live hardware mode immediately isolates corrupted/text telemetry."""
    adapter = SensorAdapter(port="TEST")
    adapter.daemon.simulation_active = False

    adapter._packet_ingestion_callback(("corrupted_signal", 0.1, 0.1, 0.1))

    assert adapter.frames_dropped == 1
    assert adapter.frames_received == 0


def test_simulation_boundary_allows_synthetic_over_voltage_frame():
    """Verify simulation fallback loop bypasses the clipping safety gate."""
    adapter = SensorAdapter(port="TEST")
    adapter.daemon.simulation_active = True

    adapter._packet_ingestion_callback((2.0480, 0.1, 0.1, 0.1))

    assert adapter.frames_dropped == 0
    assert adapter.frames_received == 1


# =====================================================================
# 2. RUNTIME LIFECYCLE STATE TRANSITIONS (Fail-Safe Verification)
# =====================================================================

def test_lifecycle_transition_engages_simulation_active_on_serial_fault(monkeypatch):
    """Verify a connection error transitions state cleanly to simulation fallback."""
    daemon = HardwareSerialDaemon(use_mock_fallback=True)
    daemon.running = True
    observed = {}

    def fake_serial_fault(*args, **kwargs):
        raise serial.SerialException("Physical USB Port Disconnected")

    def fake_simulation_carrier_loop():
        observed["simulation_active"] = daemon.simulation_active
        daemon.running = False

    monkeypatch.setattr("serial_daemon.serial.Serial", fake_serial_fault)
    monkeypatch.setattr(daemon, "_simulation_carrier_loop", fake_simulation_carrier_loop)

    daemon._lifecycle_loop()

    assert observed["simulation_active"] is True
    assert daemon.simulation_active is True


def test_lifecycle_transition_resets_simulation_active_on_hardware_lock(monkeypatch):
    """Verify a successful serial lock cleanly switches simulation back to False."""
    daemon = HardwareSerialDaemon(use_mock_fallback=True)
    daemon.running = True
    daemon.simulation_active = True

    mock_serial_stream = mock.MagicMock()
    mock_serial_stream.readline.side_effect = [b"V1:1.0,V2:1.0,V3:1.0,V4:1.0,CRC:0xAA\n"]

    def fake_serial_lock(*args, **kwargs):
        return mock_serial_stream

    original_process = daemon.process_raw_line

    def wrap_process_execution(*args, **kwargs):
        result = original_process(*args, **kwargs)
        daemon.running = False
        return result

    monkeypatch.setattr("serial_daemon.serial.Serial", fake_serial_lock)
    monkeypatch.setattr(daemon, "process_raw_line", wrap_process_execution)

    daemon._lifecycle_loop()
    assert daemon.simulation_active is False
