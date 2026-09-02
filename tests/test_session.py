#!/usr/bin/env python3
"""Phase 10: Test Matrix for Session Orchestration Modules."""
import numpy as np
import pytest
from run_session import UnifiedVivicSession

def test_session_orchestration_matrix_pass():
    """Validates full integration path: data ingestion -> optimization -> latent tracking."""
    session = UnifiedVivicSession(port="TEST_ORCH_PORT")
    rng = np.random.default_rng(seed=202)

    # Force saturate the underlying adapter structures past the 1280 limit
    for _ in range(1282):
        v1, v2, v3, v4 = rng.normal(0, 1), rng.normal(0, 1), rng.normal(0, 1), rng.normal(0, 1)
        packet = f"V1:{v1},V2:{v2},V3:{v3},V4:{v4}\n"
        session.engine.adapter.process_incoming_packet(packet)

    # Step through a single manual tracking step loop explicitly to check metric key consistency
    # P1 OPTIMIZATION: Unpack both the loss value and the reused latent vector token natively
    loss_val, latent_vector = session.engine.train_step()
    assert loss_val >= 0.0
    assert latent_vector is not None
