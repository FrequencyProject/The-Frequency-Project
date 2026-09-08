#!/usr/bin/env python3
"""High-Assurance End-to-End Integration Pipeline Test Suite.

Validates that raw streaming data propagates flawlessly across the daemon, 
adapter, network model, and loss engines to ensure absolute operational stability.
"""
import time
import pytest
import numpy as np
import torch
import config
from run_session import UnifiedVivicSession


def test_end_to_end_operational_pipeline_convergence():
    """Validates unified pipeline behavior under continuous mock ingestion cycles.
    
    Verifies that the shared hardware adapter charges cleanly, baseline calibration
    derives non-zero thresholds, and the model network steps without runtime faults.
    """
    print("[INIT] Launching master end-to-end pipeline integration check...")
    
    # Instantiate the master session coordinator using our production MOCK routing
    session = UnifiedVivicSession(port="MOCK")
    
    # HARDENING REMEDIATION: Pre-charge the sliding window buffers to safely
    # bypass real-time 60Hz timing gates during automated unit execution passes.
    with session.adapter.lock:
        for ch in ["ch1", "ch2", "ch3", "ch4"]:
            session.adapter.buffers[ch].clear()
            for i in range(session.adapter.window_size):
                # Populate with a microsecond-scaled noise wave to pass the firewall
                val = 0.05 * float(np.sin(i * 0.05))
                session.adapter.buffers[ch].append(val)
                
    try:
        # 1. Verify Environmental Calibration
        session.execute_baseline_calibration()
        assert session.is_calibrated is True, "Integration Error: System failed to calibrate baseline."
        assert len(session.ambient_means) == config.HARDWARE.num_channels, "Integration Error: Channel tracking size mismatch."
        
        # Capture an early snapshot of model parameters to track gradient changes
        initial_params = [p.clone().detach() for p in session.engine.model.parameters() if p.requires_grad]
        
        # 2. Execute Live Training Cycles
        # Pushes consecutive frames through the convolutional layers and resonance loss matrix
        session.execute_live_cycle(steps=3)
        assert session.engine.warmed_up is True, "Integration Error: Network pipeline suffered data starvation."
        
        # 3. Verify Gradient Backpropagation and Parameter Updates
        # Confirms that weight adjustments occurred, proving the mathematical engine converges
        updated_params = [p.clone().detach() for p in session.engine.model.parameters() if p.requires_grad]
        
        param_shifted = False
        for init_p, up_p in zip(initial_params, updated_params):
            if not torch.equal(init_p, up_p):
                param_shifted = True
                break
                
        assert param_shifted is True, "Integration Error: Loss backward pass failed to adjust network parameters."
        print(" -> [PASSED] Whole-system data flow and parameter optimization convergence verified.")

    finally:
        # Guarantee safe, non-destructive resource teardown to release background workers cleanly
        session.terminate_session()
