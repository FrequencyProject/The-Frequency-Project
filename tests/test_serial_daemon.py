import numpy as np
from serial_daemon import HardwareSerialDaemon


def test_parser():
    d = HardwareSerialDaemon()
    assert d.parse_raw_line("V1:1.0,V2:2.0,V3:3.0,V4:4.0") is not None
