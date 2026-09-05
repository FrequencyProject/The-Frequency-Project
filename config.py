#!/usr/bin/env python3
"""Global System Configuration Parameters.

Centralizes all hardware and model constraints to ensure long-term 
maintainability and allow scaling without code-level modifications.
"""

# Hardware & Sampling Constraints
NUM_CHANNELS = 4
WINDOW_SIZE = 1280
SAMPLING_RATE_HZ = 60.0

# Deep Learning Parameters
LATENT_DIMENSION = 128
LEARNING_RATE = 1e-3
WEIGHT_DECAY = 1e-4
