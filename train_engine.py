#!/usr/bin/env python3
"""Phase 3: Deep Learning Training Engine.

Bridges the MultiChannelSensorAdapter ingestion pipeline to the PyTorch
neural network architecture and optimizes weights using ResonanceCoherenceLoss.
"""
import time
import torch
import torch.optim as optim
import numpy as np
from sensor_adapter import MultiChannelSensorAdapter
from model_architecture import AsymmetricSpatialEncoder
from resonance_loss import ResonanceCoherenceLoss


class VivicTrainingEngine:
    """Manages real-time data streaming execution and model parameter updates."""

    def __init__(self, port: str = "MOCK", latent_dim: int = 128, lr: float = 0.001):
        self.adapter = MultiChannelSensorAdapter(port=port, window_size=1280, debug=False)
        self.model = AsymmetricSpatialEncoder(latent_dim=latent_dim)
        self.loss_fn = ResonanceCoherenceLoss()

        # Optimize neural weights to match environmental geometry constraints
        self.optimizer = optim.AdamW(self.model.parameters(), lr=lr, weight_decay=1e-4)

    def train_step(self) -> float:
        """Executes a single optimization step from the running telemetry queues."""
        self.model.train()

        # Pull the clean, row-normalized (4, 1280) float32 matrix tensor from memory deques
        features = self.adapter.get_ai_features()

        # Verify the rolling window has saturated completely before updating parameters
        if np.all(features == 0.0):
            return -1.0  # Buffer warm-up state active, skip step

        # Convert the NumPy matrix payload into a PyTorch batch tracking tensor
        # Input Shape: (1, 4, 1280) -> Batch Size of 1
        tensor_in = torch.from_numpy(features).unsqueeze(0)

        self.optimizer.zero_grad()

        # Forward Pass: Extract the non-semantic latent vector
        latent_vector = self.model(tensor_in)

        # Loss Optimization: Calculate continuous Planetary Divergence Index (PDI)
        loss = self.loss_fn(latent_vector)

        # Backward Pass: Backpropagate the gradient vectors and step weights
        loss.backward()
        self.optimizer.step()

        return loss.item()

    def run_active_session(self, steps: int = 5, step_delay_s: float = 0.1):
        """Launches background ports ingestion threads and steps through an optimization run."""
        print("[TRAIN_ENGINE] Activating hardware background telemetry ingestion...")
        self.adapter.start_ingestion()
        time.sleep(0.5)  # Allow underlying serial daemon ports thread settling window

        print(f"[TRAIN_ENGINE] Starting active training session ({steps} targeted cycles)...")
        try:
            completed_steps = 0
            while completed_steps < steps:
                loss_val = self.train_step()
                if loss_val < 0.0:
                    print(" -> Telemetry queue saturating... warming memory buffers.")
                    time.sleep(0.2)
                    continue

                completed_steps += 1
                perf = self.adapter.metrics.get("last_processing_time_ms", 0.0)
                print(
                    f" -> [CYCLE {completed_steps}/{steps}] PDI Loss: {loss_val:.6f} | Execution: {perf:.2f}ms"
                )
                time.sleep(step_delay_s)

        finally:
            print("[TRAIN_ENGINE] Halting background physical interface processes safely...")
            self.adapter.stop_ingestion()


if __name__ == "__main__":
    print("[INIT] Launching Training Engine runtime validation check...")
    # Initialize the engine to parse mock telemetry streams
    engine = VivicTrainingEngine(port="MOCK_TEST")

    # Pre-saturate the adapter's collections.deque structures with realistic mock strings
    # to bypass the window warm-up gate instantly for local script validation
    rng = np.random.default_rng(seed=42)
    for _ in range(1280):
        # Emulate the explicit string format required by the parser
        ch1, ch2, ch3, ch4 = rng.normal(0, 1), rng.normal(0, 1), rng.normal(0, 1), rng.normal(0, 1)
        mock_packet = f"V1:{ch1},V2:{ch2},V3:{ch3},V4:{ch4}\n"
        engine.adapter.process_incoming_packet(mock_packet)

    # Execute a clean execution run block
    engine.run_active_session(steps=3, step_delay_s=0.01)
    print("[SUCCESS] Deep learning execution training engine verified for integration.")
