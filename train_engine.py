#!/usr/bin/env python3
"""Phase 4: Deep Learning Training Engine.

Bridges the SensorAdapter ingestion pipeline to the PyTorch neural network 
architecture and optimizes weights using ResonanceCoherenceLoss with device agility.
"""
import time
import logging
import torch
import torch.optim as optim
import numpy as np
from sensor_adapter import SensorAdapter
from model_architecture import AsymmetricSpatialEncoder
from resonance_loss import ResonanceCoherenceLoss

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')
logger = logging.getLogger("TrainingEngine")


class VivicTrainingEngine:
    """Manages real-time data streaming execution and model parameter updates with hardware acceleration."""

    def __init__(self, port: str = "MOCK", latent_dim: int = 128, lr: float = 0.001):
        # PRODUCTION HARDENING: Automatically locate and exploit accelerated hardware nodes if present
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Initializing optimization target tracking engine on device: {self.device}")

        # Integration Realignment: Instantiate standard SensorAdapter passing parameter wildcards smoothly
        self.adapter = SensorAdapter(port=port, window_size=1280)
        
        # Load model architecture and push parameter parameters straight to the active hardware block
        self.model = AsymmetricSpatialEncoder(latent_dim=latent_dim).to(self.device)
        self.loss_fn = ResonanceCoherenceLoss()

        # Optimize neural weights to match environmental geometry constraints
        self.optimizer = optim.AdamW(self.model.parameters(), lr=lr, weight_decay=1e-4)

    def train_step(self) -> float:
        """Executes a single optimization step from the running telemetry queues with device safety."""
        self.model.train()

        # Pull the clean, row-normalized (4, 1280) float32 matrix from memory deques
        features = self.adapter.get_ai_features()

        # Verify the rolling window has saturated completely before updating parameters
        if np.all(features == 0.0):
            return -1.0  # Buffer warm-up state active, skip step

        # Reset gradient tracking tensors inside optimization pools to clear calculation memory footprints
        self.optimizer.zero_grad()

        # Convert the NumPy matrix payload into a PyTorch batch tracking tensor and map to the active device
        # Input Shape: (1, 4, 1280) -> Batch Size of 1
        tensor_in = torch.from_numpy(features).unsqueeze(0).to(self.device)

        # Forward Pass: Extract the non-semantic latent vector
        latent_vector = self.model(tensor_in)

        # Loss Optimization: Calculate continuous Planetary Divergence Index (PDI)
        loss = self.loss_fn(latent_vector)

        # Backward Pass: Backpropagate the gradient vectors and step weights securely
        loss.backward()
        self.optimizer.step()

        return loss.item()

    def run_active_session(self, steps: int = 5, step_delay_s: float = 0.1):
        """Launches background acquisition threads and steps through an interruptible optimization run."""
        logger.info("Activating hardware background telemetry ingestion...")
        # INTEGRATION REALIGNMENT: Correct public method method endpoints called on the adapter
        self.adapter.start_acquisition()
        time.sleep(0.5)  # Allow underlying serial daemon ports thread settling window

        logger.info(f"Starting active training session ({steps} targeted cycles)...")
        try:
            completed_steps = 0
            while completed_steps < steps:
                t_start = time.perf_counter()
                loss_val = self.train_step()
                if loss_val < 0.0:
                    logger.info("Telemetry queue saturating... warming memory buffers.")
                    time.sleep(0.2)
                    continue

                completed_steps += 1
                elapsed_ms = (time.perf_counter() - t_start) * 1000.0
                logger.info(
                    f" -> [CYCLE {completed_steps}/{steps}] PDI Loss: {loss_val:.6f} | Execution: {elapsed_ms:.2f}ms"
                )
                time.sleep(step_delay_s)

        finally:
            logger.info("Halting background physical interface processes safely...")
            # INTEGRATION REALIGNMENT: Correct public endpoint teardown handler
            self.adapter.stop_acquisition()


if __name__ == "__main__":
    logger.info("Launching Training Engine runtime validation check...")
    engine = VivicTrainingEngine(port="MOCK_TEST")

    # Pre-saturate the adapter structures to bypass the buffer warm-up gate instantly
    rng = np.random.default_rng(seed=42)
    for _ in range(1280):
        ch1, ch2, ch3, ch4 = rng.normal(0, 1), rng.normal(0, 1), rng.normal(0, 1), rng.normal(0, 1)
        mock_packet = f"V1:{ch1},V2:{ch2},V3:{ch3},V4:{ch4}\n"
        engine.adapter.process_incoming_packet(mock_packet)

    # Execute a clean execution run block
    engine.run_active_session(steps=3, step_delay_s=0.01)
    logger.info("Deep learning execution training engine verified for integration.")
