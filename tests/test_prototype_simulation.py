#!/usr/bin/env python3
"""High-Assurance Unit Test Suite for the Prototype Simulation Harness.

Verifies end-to-end signal compilation, firewalls, and data bounds.
"""
from prototype_simulation import run_simulation_smoke_test

def test_prototype_simulation_harness_lifecycle():
    """Asserts that the complete validation pipeline passes standard, flatline, and firewall checks."""
    # Run the comprehensive simulation pass natively
    run_simulation_smoke_test()
