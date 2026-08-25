#!/usr/bin/env python3
"""Unit test suite for verification of Phase 3 Unified Session wrappers."""
import numpy as np
import torch
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
    loss_val = session.engine.train_step()
    assert loss_val >= 0.0

    features = session.engine.adapter.get_ai_features()
    latent_vector = session.engine.model(torch.from_numpy(features).unsqueeze(0))
    metrics = session.monitor.evaluate_vector(latent_vector.detach().cpu().numpy())

    assert metrics["step"] == 1
    assert "euclidean_delta" in metrics
    assert "cosine_similarity" in metrics
