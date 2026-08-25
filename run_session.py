#!/usr/bin/env python3
"""Phase 3: Unified Cybernetic Training and Monitoring Orchestrator.

Ties the real-time data streaming ingestion pipeline, PyTorch training loops, 
and high-dimensional latent trajectory monitor together into a unified execution context.
"""
import time
import torch
import numpy as np
from train_engine import VivicTrainingEngine
from latent_monitor import VivicLatentMonitor


class UnifiedVivicSession:
    """Orchestrates live telemetry ingestion, weight optimization, and latent space tracking."""

    def __init__(self, port: str = "MOCK", latent_dim: int = 128, lr: float = 0.001):
        # 1. Initialize the core training loop infrastructure
        self.engine = VivicTrainingEngine(port=port, latent_dim=latent_dim, lr=lr)

        # 2. Initialize the hyper-dimensional trajectory monitoring metrics engine
        self.monitor = VivicLatentMonitor(latent_dim=latent_dim, threshold_sigma=3.0)

    def execute_live_cycle(self, steps: int = 10, cycle_delay_s: float = 0.1):
        """Launches the ingestion daemons and prints unified telemetry metrics live."""
        print("======================================================================")
        # Convert absolute date presentation for scheduled relative tracking flags
        print(f"VIVIC AI: ACTIVE UNIFIED COGNITIVE MONITOR SESSION")
        print("======================================================================")
        print("[ORCHESTRATOR] Starting background hardware acquisition networks...")

        # Activate underlying serial threads via the sensor adapter bounds
        self.engine.adapter.start_ingestion()
        time.sleep(0.5)  # Physical UART line settling safety window

        print(
            f"[ORCHESTRATOR] Entering active training & trajectory monitoring loop ({steps} cycles)..."
        )
        try:
            completed_cycles = 0
            while completed_cycles < steps:
                # 1. Execute an unsupervised optimization backprop pass step
                loss_val = self.engine.train_step()

                # Check if buffer warm-up gate is active
                if loss_val < 0.0:
                    print(" -> Deque structures warming... saturating fixed window depth.")
                    time.sleep(0.2)
                    continue

                completed_cycles += 1

                # 2. Extract the fresh latent vector slice under no-grad evaluation mode
                self.engine.model.eval()
                features = self.engine.adapter.get_ai_features()
                tensor_in = torch.from_numpy(features).unsqueeze(0)

                with torch.no_grad():
                    latent_vector = self.engine.model(tensor_in)

                # Convert the PyTorch output to a NumPy array for clean tracking processing
                latent_np = latent_vector.cpu().numpy()

                # 3. Pipe the latent payload directly into the monitor trajectory loops
                metrics = self.monitor.evaluate_vector(latent_np)

                # 4. Extract performance profiling indicators from the adapter metrics
                perf_ms = self.engine.adapter.metrics.get("last_processing_time_ms", 0.0)

                # Output a structured, unembellished, zero-dependency telemetry log
                alert_status = "⚠️ [RESONANCE ALERT]" if metrics["is_anomaly"] else "[HEALTHY]"
                print(
                    f" -> [STEP {completed_cycles}/{steps}] "
                    f"PDI Loss: {loss_val:.6f} | "
                    f"Velocity: {metrics['euclidean_delta']:.4f} | "
                    f"Drift: {metrics['cosine_similarity']:.4f} | "
                    f"Compute: {perf_ms:.2f}ms | "
                    f"State: {alert_status}"
                )

                time.sleep(cycle_delay_s)

        except KeyboardInterrupt:
            print("\n[ORCHESTRATOR WARNING] Manual session interruption captured.")
        finally:
            print(
                "[ORCHESTRATOR] Halting hardware port acquisitions and tearing down threads safely..."
            )
            self.engine.adapter.stop_ingestion()
            print("======================================================================")
            print(
                f"[SUCCESS] Session terminated. Total Vectors Monitored: {self.monitor.total_vectors_monitored}"
            )
            print("======================================================================")


if __name__ == "__main__":
    # Test harness to verify total integration state integrity locally
    print("[INIT] Launching Unified Orchestrator runtime verification check...")
    session = UnifiedVivicSession(port="MOCK_TEST")

    # Pre-saturate memory deques using mock strings to instantly bypass the warm-up gate
    rng = np.random.default_rng(seed=42)
    for _ in range(1280):
        ch1, ch2, ch3, ch4 = rng.normal(0, 1), rng.normal(0, 1), rng.normal(0, 1), rng.normal(0, 1)
        mock_packet = f"V1:{ch1},V2:{ch2},V3:{ch3},V4:{ch4}\n"
        session.engine.adapter.process_incoming_packet(mock_packet)

    # Execute a clean 3-step validation cycle
    session.execute_live_cycle(steps=3, cycle_delay_s=0.01)
