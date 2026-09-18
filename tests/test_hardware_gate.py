import pytest
from unittest.mock import patch, MagicMock
from verify_hardware_gate import execute_preflight_hardware_scan


def test_hardware_gate_success_path():
    """Validates that a matching, active serial port passes the pre-flight readiness gate."""
    mock_port = MagicMock()
    mock_port.device = "COM3"

    with patch("serial.tools.list_ports.comports", return_value=[mock_port]), \
            patch("serial.Serial") as mock_serial:

        # Configure the mock serial context manager to simulate an open port connection
        mock_serial.return_value.__enter__.return_value.is_open = True

        result = execute_preflight_hardware_scan(target_port="COM3", max_discovery_wait_seconds=0.1)
        assert result is True


def test_hardware_gate_timeout_fallback_path():
    """Ensures the sequencer signals a software simulation fallback when a port is absent."""
    with patch("serial.tools.list_ports.comports", return_value=[]):
        result = execute_preflight_hardware_scan(target_port="COM3", max_discovery_wait_seconds=0.1)
        assert result is False
