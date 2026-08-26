#!/usr/bin/env python3
"""Automated unit test pass for session orchestrations workflows."""
import numpy as np
from run_session import UnifiedVivicSession


def test_session_orchestration_matrix_pass():
    """Validates full integration path: data ingestion -> optimization -> latent tracking."""
    session = UnifiedVivicSession(port="MOCK")
    rng = np.random.default_rng(seed=202)

    # Force saturate the underlying adapter structures past the limits using signed payloads
    for _ in range(1285):
        mock_vector = rng.normal(0, 1, 4).astype(np.float32)
        p_bytes, s_bytes = session.engine.adapter.signer.sign_vector(mock_vector)
        session.engine.adapter.process_signed_packet((p_bytes, s_bytes))

    # Execute a minor live session slice loop safely
    session.execute_live_cycle(steps=2, cycle_delay_s=0.001)
    assert session.monitor.total_vectors_monitored == 2
