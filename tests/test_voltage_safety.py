from sensor_adapter import SensorAdapter


def test_live_mode_drops_saturated_frame():
    adapter = SensorAdapter(port="TEST")
    adapter.daemon.running = True
    adapter.daemon.simulation_active = False

    adapter._packet_ingestion_callback((2.0480, 0.1, 0.1, 0.1))

    assert adapter.frames_dropped == 1
    assert adapter.frames_received == 0
    assert adapter._count == 0


def test_live_mode_drops_non_numeric_frame():
    adapter = SensorAdapter(port="TEST")
    adapter.daemon.running = True
    adapter.daemon.simulation_active = False

    adapter._packet_ingestion_callback(("invalid", 0.1, 0.1, 0.1))

    assert adapter.frames_dropped == 1
    assert adapter.frames_received == 0
    assert adapter._count == 0


def test_simulation_mode_allows_synthetic_boundary_value():
    adapter = SensorAdapter(port="TEST")
    adapter.daemon.running = True
    adapter.daemon.simulation_active = True

    adapter._packet_ingestion_callback((2.0480, 0.1, 0.1, 0.1))

    assert adapter.frames_dropped == 0
    assert adapter.frames_received == 1
    assert adapter._count == 1
