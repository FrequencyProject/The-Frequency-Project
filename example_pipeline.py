#!/usr/bin/env python3
"""End-to-End Operational Pipeline Tutorial.

Demonstrates the primary integration pathway by connecting raw serial line parsing, 
circular buffering, 1D-CNN spatial encoding, and statistical anomaly tracking.
"""
import torch
import numpy as np
from sensor_adapter import SensorAdapter
from model_architecture import AsymmetricSpatialEncoder
from latent_monitor import VivicLatentMonitor


def run_integrated_pipeline_tutorial():
    print("======================================================================")
    print("TELEMETRY INGESTION AND DEEP LEARNING ANALYSIS PIPELINE")
    print("======================================================================\n")

    # 1. Initialize Spatial Neural Network Structure
    print("[STEP 1/4] Allocating 1D-CNN Spatial Encoder...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = AsymmetricSpatialEncoder(latent_dim=128).to(device)
    model.eval()  # Switch network layers cleanly to evaluation/inference mode
    print(f" -> Execution device: {device}")
    print(" -> Model memory successfully allocated.\n")

    # 2. Initialize the Rolling Buffer Sensor Adapter Layer
    print("[STEP 2/4] Initializing thread-safe Sensor Adapter...")
    # Instantiate with a window size of 1280 samples matching our operational footprint
    adapter = SensorAdapter(port="MOCK_TUTORIAL_PORT", window_size=1280)
    print(f" -> Circular buffer allocated for 4 channels (window_size={adapter.window_size}).\n")

    # 3. Initialize the Statistical Anomaly Monitor
    print("[STEP 3/4] Instantiating Latent Space Variance Monitor...")
    monitor = VivicLatentMonitor(latent_dim=128, history_len=20)
    print(" -> Statistical tracking registers initialized.\n")

    # 4. Simulate Live High-Frequency Ingestion Processing Loops via Public Endpoints
    print("[STEP 4/4] Running baseline telemetry ingestion loop...")
    print(" -> Saturating circular buffer windows with simulated baseline frames...")
    
    rng = np.random.default_rng(seed=42)
    for _ in range(1280):
        # Generate random baseline values
        v1 = float(rng.normal(0.0, 0.1))
        v2 = float(rng.normal(0.0, 0.1))
        v3 = float(rng.normal(0.0, 0.1))
        v4 = float(rng.normal(0.0, 0.1))
        
        # Build raw string payload matching the exact output layout of the ESP32-S3 C++ firmware
        mock_raw_frame = f"V1:{v1:.4f},V2:{v2:.4f},V3:{v3:.4f},V4:{v4:.4f}\n"
        
        # Public data contract method handles string decoding, parsing, and circular buffering
        adapter.process_incoming_packet(mock_raw_frame)
        
    print(" -> Ingestion memory matrices fully saturated.")

    # 5. Extract snapshot matrices, map to PyTorch, and evaluate anomalies
    print("\n -> Triggering end-to-end tensor inference step...")
    with torch.no_grad():
        # A. Pull the thread-safe, normalized Z-score feature snapshot out of the adapter circular view
        compiled_features = adapter.get_ai_features()  # Returns shape (4, 1280)
        
        # B. Convert the arrays cleanly into a device-native single-precision tensor profile
        torch_tensor = torch.tensor(compiled_features, dtype=torch.float32, device=device)
        
        # C. Map the waveform matrix straight through the 1D-CNN convolutional layers
        latent_output = model(torch_tensor)  # Emits high-dimensional shape (1, 128)
        
        # D. Unwrap the latent array to pass its vector cleanly into the anomaly filters
        unwrapped_vector = latent_output.squeeze(0).cpu().numpy()
        
        # E. Process through the 3-Sigma alert perimeter tracking logic
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
