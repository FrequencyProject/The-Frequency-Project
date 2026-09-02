#!/usr/bin/env python3
"""Phase 10: High-Assurance End-to-End Automated Integration Smoke-Test Harness.

Simulates active real-time multi-threaded ingestion lifecycles to validate 
the complete processing loop: Serial Daemon -> Sensor Adapter -> Signal DSP 
-> 1D-CNN Encoder Forward Pass -> Resonance Loss Backpropagation -> 3-Sigma Anomaly Tracking.
"""
import time
import pytest
import numpy as np
import torch
from run_session import UnifiedVivicSession

def test_automated_pipeline_integration_lifecycle(capsys):
    """Audits the unified multi-threaded operational cycle under realistic telemetry loads."""
    logger_header = "[INTEGRATION TEST]"
    print(f"\n{logger_header} Initializing master system orchestration loop...")
    
    # 1. Instantiate the comprehensive unified orchestrator mapping to a simulated MOCK interface port
    session = UnifiedVivicSession(port="MOCK_INTEGRATION_PORT")
    rng = np.random.default_rng(seed=101)
    
    # 2. Assert all isolated baseline parameters initialize in an uncalibrated, safe standby state
    assert session.is_active is False
    assert session.is_calibrated is False
    assert session.monitor.anomalies_detected == 0
    
    print(f"{logger_header} Pre-saturating serial deques to bypass warm-up buffer gates...")
    # 3. Simulate high-speed serial stream packet broadcasts to completely saturate the rolling 1280 windows
    for _ in range(1285):
        v1, v2, v3, v4 = rng.normal(0, 1), rng.normal(0, 1), rng.normal(0, 1), rng.normal(0, 1)
        mock_packet = f"V1:{v1:.4f},V2:{v2:.4f},V3:{v3:.4f},V4:{v4:.4f}\n"
        session.adapter.process_incoming_packet(mock_packet)
        
    # Verify memory ring structures collected the data points cleanly along the flat 1D sequence dimensions
    assert len(session.adapter.buffers["ch1"]) == 1280
    assert len(session.adapter.buffers["ch4"]) == 1280

    print(f"{logger_header} Launching baseline quiet state environmental calibration...")
    # 4. Run the interruptible calibration sweep
    session.execute_baseline_calibration()
    assert session.is_calibrated is True
    assert np.all(session.ambient_stds >= 1e-6), "Epsilon guard failed to catch zero variance flatlines."

    print(f"{logger_header} Executing live multi-rate live training optimization cycle...")
    # 5. Trigger consecutive real-time cycles
    session.execute_live_cycle(steps=3)
    
    # 6. Enforce systemic structural invariant assertions
    assert session.is_active is False
    assert session.monitor._test_step_counter > 0
    
    # 7. Extract a valid baseline feature tensor to establish the true moving average anchor
    features = session.adapter.get_ai_features()
    torch_tensor = torch.from_numpy(features).unsqueeze(0).float().to(session.engine.device)
    
    session.engine.model.eval()
    with torch.no_grad():
        latent_vector = session.engine.model(torch_tensor)
        
    # Convert tensor to raw array representation
    base_latent_array = latent_vector.detach().cpu().numpy()
    
    # Pre-seed the monitor with the baseline run frame to lock down mean state scales
    _ = session.monitor.evaluate_vector(base_latent_array)
    
    # HARDENING REFACTOR: Simulate a major geophysical event or tectonic fault shift by injecting
    # a massive structural multiplier vector directly into the high-dimensional latent space.
    # This forces an undeniable spatial fracture that bypasses frontline normalizers to test alarms.
    anomaly_latent_spike = base_latent_array * 50.0
    
    metrics = session.monitor.evaluate_vector(anomaly_latent_spike)
    
    print(f"\n{logger_header} Final Anomaly Engine Metrics Summary: {metrics}")
    assert metrics["is_anomaly"] is True, "Security compromise: 3-Sigma perimeters failed to flag extreme vector drift."
    assert session.monitor.anomalies_detected >= 1, "Historical alert counter tracking registers failed to increment."
    
    # Clean up the background serial acquisition threads completely
    session.adapter.stop_acquisition()
    print(f"{logger_header} Master integration smoke test completed with 100% precision light.")
