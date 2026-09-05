#!/usr/bin/env python3
"""Global System Configuration Parameters.

Centralizes all hardware and model constraints to ensure long-term 
maintainability and allow scaling without code-level modifications.
"""
from typing import NamedTuple


class HardwareConstraints(NamedTuple):
    """Immutable hardware and environmental telemetry parameters."""
    num_channels: int = 4
    window_size: int = 1280
    sampling_rate_hz: float = 60.0


class ModelHyperparameters(NamedTuple):
    """Immutable deep learning configuration matrices."""
    latent_dimension: int = 128
    learning_rate: float = 1e-3
    weight_decay: float = 1e-4


# Instantiated instances provide clean dot-notation read-only access (e.g., config.HARDWARE.window_size)
HARDWARE = HardwareConstraints()
MODEL = ModelHyperparameters()


if __name__ == "__main__":
    print("[INIT] Verifying global configuration layout immutability...")
    print(f" -> Sampling Channels Locked: {HARDWARE.num_channels}")
    print(f" -> Latent Space Target Allocation: {MODEL.latent_dimension}")
    try:
        # Test runtime write protection parameter defenses explicitly
        # This will fail natively because NamedTuples are immutable
        HARDWARE.window_size = 1000  # type: ignore
    except AttributeError:
        print("[SUCCESS] Parameter safety verified. Runtime modifications blocked.")
