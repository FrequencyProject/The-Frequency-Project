def test_prototype_whole_system_integration():
    """Asserts that the whole system orchestrator calibrates and steps without resource locks."""
    from run_session import UnifiedVivicSession
    import numpy as np
    
    session = UnifiedVivicSession(port="MOCK")
    
    # HARDENING REMEDIATION: Pre-charge deques to break the 21-second timing bottleneck.
    # Instantly jams 1280 floating-point numbers into the double-ended queues, bypasses 
    # the clock starvation loop, and accelerates the PyTest suite execution down to milliseconds.
    for ch in ["ch1", "ch2", "ch3", "ch4"]:
        for _ in range(session.adapter.window_size):
            session.adapter.buffers[ch].append(0.1) # Prime with neutral ambient noise profiles
            
    try:
        # Run calibration—will now see the deques as completely full and execute immediately
        session.execute_baseline_calibration()
        assert session.is_calibrated is True
        
        # Step through optimization loops
        session.execute_live_cycle(steps=2)
        assert session.engine.warmed_up is True
        
    finally:
        session.terminate_session()
