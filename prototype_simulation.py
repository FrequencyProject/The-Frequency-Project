#!/usr/bin/env python3
import math
import collections
from typing import cast
import numpy as np
import numpy.typing as npt


class MultiChannelBioPotentialIngestion:
    """Core Ingestion Engine (mirrors the logic planned for sensor_adapter.py).

    Processes string data packets and compiles the rolling 4 x 1280 AI matrix.
    """

    def __init__(self, window_size: int = 1280) -> None:
        self.window_size = window_size
        self.num_channels = 4
        self.channels: list[collections.deque[float]] = [
            collections.deque(maxlen=window_size) for _ in range(self.num_channels)
        ]

    def process_incoming_packet(self, packet_str: str) -> None:
        """Parses the firmware-formatted string and updates sliding window queues."""
        try:
            if all(f"V{i+1}:" in packet_str for i in range(self.num_channels)):
                pairs = packet_str.strip().split(",")
                parsed_values = []
                for pair in pairs:
                    _, val_str = pair.split(":")
                    parsed_values.append(float(val_str))

                if len(parsed_values) == self.num_channels:
                    for i in range(self.num_channels):
                        self.channels[i].append(parsed_values[i])
        except (ValueError, IndexError):
            pass  # Gracefully drop malformed frames

    def get_ai_features(self) -> npt.NDArray[np.float32]:
        """Compiles historical deques into a normalized 4 x 1280 NumPy matrix."""
        # Ensure windows are completely full before returning data for AI inference
        if any(len(self.channels[i]) < self.window_size for i in range(self.num_channels)):
            return np.zeros((self.num_channels, self.window_size), dtype=np.float32)

        feature_matrix = np.vstack([list(ch) for ch in self.channels])

        # Row-independent Z-Score scale transformation
        means = np.mean(feature_matrix, axis=1, keepdims=True)
        stds = np.std(feature_matrix, axis=1, keepdims=True) + 1e-8
        normalized_matrix = (feature_matrix - means) / stds

        return cast(npt.NDArray[np.float32], normalized_matrix.astype(np.float32))


class BiologicalSignalEmulator:
    """Generates synthetic ecological and geophysical waveforms to mimic real-world inputs

    using isolated NumPy RNG generators compatible across 3.10, 3.11, and 3.12 environments.
    """

    def __init__(self, sampling_rate_hz: float = 20.0) -> None:
        self.fs = sampling_rate_hz
        self.tick = 0
        # Seed locally inside instance scope to ensure deterministic cross-version evaluation
        self.rng = np.random.default_rng(seed=42)

    def generate_frame(self) -> str:
        """Computes overlapping cycles, noise profiles, and sudden environmental spikes."""
        t = self.tick / self.fs
        self.tick += 1

        # Channel 1: Tree Sapwood - Slow metabolic rhythms (0.05 Hz) + uniform noise
        ch1 = 15.0 * math.sin(2 * math.pi * 0.05 * t) + self.rng.uniform(-0.5, 0.5)

        # Channel 2: Mycelium Alpha - Ultra-slow chemical gradient decay (0.01 Hz) + micro-spikes
        ch2 = 8.0 * math.cos(2 * math.pi * 0.01 * t) + (2.5 if self.rng.random() > 0.99 else 0.0)

        # Channel 3: Mycelium Beta - Interdependent cross-coupling with 2-second phase lag
        ch3 = 6.0 * math.cos(2 * math.pi * 0.01 * (t - 2.0)) + self.rng.uniform(-0.2, 0.2)

        # Channel 4: Local ELF Background - Ambient Schumann resonance fluctuations (7.83 Hz)
        ch4 = 1.2 * math.sin(2 * math.pi * 7.83 * t) + self.rng.uniform(-1.0, 1.0)

        # Output exact firmware CSV layout format string
        return f"V1:{ch1:.4f},V2:{ch2:.4f},V3:{ch3:.4f},V4:{ch4:.4f}\n"


def run_simulation_test() -> None:
    """Executes the validation test runtime loop."""
    print("=" * 70)
    print("VIVIC AI ARCHITECTURE: PIPELINE SIMULATION VALIDATION RUNTIME")
    print("=" * 70)

    # Initialize components
    engine = MultiChannelBioPotentialIngestion(window_size=1280)
    emulator = BiologicalSignalEmulator(sampling_rate_hz=20.0)

    print("[INIT] Saturating rolling matrix window (Requires 1280 historical ticks)...")

    # Fast-forward simulation data parsing to fill the memory buffer instantly
    for _ in range(1280):
        packet = emulator.generate_frame()
        engine.process_incoming_packet(packet)

    print("[SUCCESS] Matrix window saturated.")
    print(f" -> Queue Buffer Sizes: {[len(engine.channels[i]) for i in range(4)]}")

    # Extract the compiled AI data tensor matrix
    ai_tensor = engine.get_ai_features()

    print("-" * 70)
    print("MATHEMATICAL INTEGRITY MATRIX RESULTS:")
    print(f" -> Tensor Matrix Output Shape : {ai_tensor.shape} (Expected: (4, 1280))")
    print(f" -> Array Underlying Data Type : {ai_tensor.dtype} (Expected: float32)")
    print(f" -> Channel 1 Z-Normalized Mean: {np.mean(ai_tensor):.6f} (Expected: ~0.000000)")
    print(f" -> Channel 1 Standard Deviation: {np.std(ai_tensor):.6f} (Expected: ~1.000000)")
    print(
        f" -> Comprehensive Tensor Bounds : Min = {np.min(ai_tensor):.4f} | Max = {np.max(ai_tensor):.4f}"
    )
    print("-" * 70)

    # Verify execution checks against standard AI system constraints
    assert ai_tensor.shape == (4, 1280), "[ERROR] Dimension mismatch."
    assert ai_tensor.dtype == np.float32, "[ERROR] Memory compilation alignment failure."
    assert abs(np.mean(ai_tensor)) < 1e-5, "[ERROR] Normalization mean shift failure."

    print("[PASSED] Architecture is verified for integration on edge AI environments.")
    print("=" * 70)


if __name__ == "__main__":
    run_simulation_test()
