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


def test_fallback_marks_simulation_active_and_calls_carrier_once():
    daemon = HardwareSerialDaemon(use_mock_fallback=True)
    daemon.running = True

    def terminate_loop_on_call():
        daemon.running = False

    with mock.patch('serial.Serial', side_effect=serial.SerialException("Serial port error")), \
            mock.patch.object(daemon, '_simulation_carrier_loop', side_effect=terminate_loop_on_call) as mock_loop:
        daemon._lifecycle_loop()
        assert daemon.simulation_active is True
        assert mock_loop.call_count == 1


def test_successful_serial_lock_resets_simulation_active():
    daemon = HardwareSerialDaemon(use_mock_fallback=True)
    daemon.running = True
    daemon.simulation_active = True

    mock_ser = mock.MagicMock()
    mock_ser.readline.side_effect = [b"V1:1.0,V2:1.0,V3:1.0,V4:1.0,CRC:0xAA\n"]

    def terminate_after_read(*args, **kwargs):
        daemon.running = False
        return mock_ser

    with mock.patch('serial.Serial', side_effect=terminate_after_read):
        daemon._lifecycle_loop()
        assert daemon.simulation_active is False
