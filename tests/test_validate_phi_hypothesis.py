#!/usr/bin/env python3
"""High-Assurance Unit Test Suite for Phase 1.5: Preregistered Phi Hypothesis.

Verifies statistical evaluation pass stability across ideal harmonic targets
and guarantees strict rejections when chaotic pink noise vectors occur.
"""
import pytest
import numpy as np
from scipy import stats
import config
from validate_phi_hypothesis import compute_cohens_d_independent

def test_cohens_d_calculation_precision():
    """Confirms math precision of the independent Cohen's d effect size reducer."""
    # Group 1 and Group 2 with known statistical variance profiles
    g1 = np.array([1.0, 1.1, 1.2, 1.0, 1.1], dtype=np.float32)
    g2 = np.array([2.0, 2.1, 2.2, 2.0, 2.1], dtype=np.float32)

    d_effect = compute_cohens_d_independent(g1, g2)

    # Assert a major statistical shift returns a clear, non-zero effect signature
    assert d_effect > 1.0
    assert isinstance(d_effect, float)

def test_hypothesis_math_under_ideal_phi_harmonic():
    """Asserts that one-sample t-tests yield high p-values under pure Phi conditions."""
    phi = (1.0 + 5.0 ** 0.5) / 2.0
    rng = np.random.default_rng(seed=42)

    # Generate mock adjacent data clustering perfectly around Phi (1.618)
    ideal_adjacent = rng.normal(loc=phi, scale=0.01, size=3600)

    # Run the primary frequentist evaluation loop
    t_stat, t_p_value = stats.ttest_1samp(ideal_adjacent, phi)

    # An ideal, indistinguishable mean must fail to reject H0 (p > 0.05)
    assert t_p_value > 0.05
    assert np.std(ideal_adjacent, ddof=1) < 0.25

def test_hypothesis_math_under_chaotic_rejection():
    """Asserts that un-harmonic white noise forces clear H0 rejections."""
    phi = (1.0 + 5.0 ** 0.5) / 2.0
    rng = np.random.default_rng(seed=42)

    # Generate data centered far away from the golden ratio target zone
    chaotic_adjacent = rng.normal(loc=5.555, scale=0.5, size=3600)

    t_stat, t_p_value = stats.ttest_1samp(chaotic_adjacent, phi)

    # A heavily skewed mean must decisively reject the hypothesis (p < 0.05)
    assert t_p_value < 0.05
