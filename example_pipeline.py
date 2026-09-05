#!/usr/bin/env python3
"""End-to-End Operational Pipeline Tutorial.

Provides outside developers with an explicit adoption pathway by connecting
the ingestion daemon, rolling sensor buffers, 1D-CNN spatial encoder inference,
and statistical 3-Sigma latent monitor in a unified execution loop.
"""
import time
import torch
import numpy as np
from serial_daemon import HardwareSerialDaemon
from sensor_adapter import SensorAdapter
from model_architecture import AsymmetricSpatialEncoder
from latent_monitor import VivicLatentMonitor


def run_integrated_pipeline_tutorial():
    print("======================================================================")
    print("VIVIC AI: END-TO-END TELEMETRY AND ANALYSIS PIPELINE TUTORIAL")
    print("======================================================================\n")

    # 1. Initialize the Core Spatial Neural Network Structure
    print("[STEP 1/4] Initializing deep learning 1D-CNN Spatial Encoder...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = AsymmetricSpatialEncoder(latent_dim=128).to(device)
    model.eval()  # Switch network layers cleanly to evaluation/inference mode
    print(f" -> Execution device locked: {device}")
    print(" -> Model dimensions successfully allocated.\n")

    # 2. Initialize the Rolling Buffer Sensor Adapter Layer
    print("[STEP 2/4] Provisioning thread-safe Sensor Adapter buffers...")
    # Instantiate with a window size of 1280 samples matching our production footprint
    adapter = SensorAdapter(port="MOCK_TUTORIAL_PORT", window_size=1280)
    print(f" -> Rolling queues allocated for 4 isolated tracks (size={adapter.window_size}).\n")

    # 3. Initialize the Statistical Anomaly Monitor
    print("[STEP 3/4] Instantiating 3-Sigma Latent Space Monitor...")
    monitor = VivicLatentMonitor(latent_dim=128, history_len=20)
    print(" -> Exponential moving variance registers primed.\n")

    # 4. Simulate Live High-Frequency Ingestion Processing Loops
    print("[STEP 4/4] Launching live telemetry processing bombardment pass...")

    # Prime our rolling ring buffer queues manually with nominal baseline waveforms 
    # to satisfy the model's un-saturated 1280 sequence footprint assertion
    print(" -> Saturating rolling memory windows with warm-up baseline metrics...")
    rng = np.random.default_rng(seed=42)
    for _ in range(1280):
        mock_packet = {
            "status": "VALID",
            "data": {
                "ch1": float(rng.normal(0.0, 0.1)),
                "ch2": float(rng.normal(0.0, 0.1)),
                "ch3": float(rng.normal(0.0, 0.1)),
                "ch4": float(rng.normal(0.0, 0.1))
            }
        }
        adapter._packet_ingestion_callback(mock_packet)
    print(" -> Ingestion memory matrices fully saturated.")

    # 5. Extract snapshot matrices, map to PyTorch, and evaluate anomalies
    print("\n -> Triggering end-to-end tensor inference step...")
    with torch.no_grad():
        # A. Pull the thread-safe, normalized Z-score feature snapshot out of the adapter
        compiled_features = adapter.get_ai_features()  # Returns shape (4, 1280)
        
        # B. Convert the arrays cleanly into a device-native single-precision tensor profile
        torch_tensor = torch.tensor(compiled_features, dtype=torch.float32, device=device)
        
        # C. Map the waveform matrix straight through the 1D-CNN convolutional layers
        latent_output = model(torch_tensor)  # Emits high-dimensional shape (1, 128)
        
        # D. Unwrap the latent array to pass its vector cleanly into the anomaly filters
        unwrapped_vector = latent_output.squeeze(0).cpu().numpy()
        
        # E. Process through the 3-Sigma alert perimeter tracking logic
        # HARDENING REMEDIATION: Capture the output as a generic result container 
        # to cleanly display the complete tracking state without type-casting failures.
        pipeline_result = monitor.evaluate_vector(unwrapped_vector)
        
        print("\n======================================================================")
        print(" PIPELINE INFERENCE EXECUTION SUCCESSFUL")
        print("======================================================================")
        print(f" -> Compiled Input Tensor Shape  : {compiled_features.shape}")
        print(f" -> Generated Latent Vector Shape: {latent_output.shape}")
        print(f" -> Telemetry Matrix Evaluation  : {pipeline_result}")
        print("======================================================================\n")


if __name__ == "__main__":
    run_integrated_pipeline_tutorial()
