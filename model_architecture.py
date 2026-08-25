#!/usr/bin/env python3
"""Phase 3: Unsupervised Deep Learning Core Layer.

Implements a Multi-Scale 1D-CNN Spatial Encoder tailored to process 
asymmetric, multi-modal ecological frequency feature tensors.
"""
import torch
import torch.nn as nn


class AsymmetricSpatialEncoder(nn.Module):
    """Processes (4, 1280) tensors using row-isolated multi-scale 1D convolutions."""

    def __init__(self, latent_dim: int = 128):
        super().__init__()

        # Branch 1: Focused feature extraction for Spectral Rows (Ch1 & Ch4)
        # Narrower kernels capture sharp frequency magnitude spikes/bin configurations
        self.spectral_conv = nn.Sequential(
            nn.Conv1d(in_channels=2, out_channels=32, kernel_size=7, stride=2, padding=3),
            nn.BatchNorm1d(32),
            nn.SiLU(),
            nn.Conv1d(in_channels=32, out_channels=64, kernel_size=5, stride=2, padding=2),
            nn.BatchNorm1d(64),
            nn.SiLU(),
            nn.AdaptiveAvgPool1d(64),  # Squash time/bin dimension to uniform depth
        )

        # Branch 2: Focused feature extraction for Temporal Rows (Ch2 & Ch3)
        # Wider receptive fields capture long-term slow-moving DC voltage transients
        self.temporal_conv = nn.Sequential(
            nn.Conv1d(in_channels=2, out_channels=32, kernel_size=25, stride=4, padding=12),
            nn.BatchNorm1d(32),
            nn.SiLU(),
            nn.Conv1d(in_channels=32, out_channels=64, kernel_size=15, stride=2, padding=7),
            nn.BatchNorm1d(64),
            nn.SiLU(),
            nn.AdaptiveAvgPool1d(64),
        )

        # Unified Fusion Layer: Blends both domain profiles into a single latent vector
        # Combined features = 64 (spectral channels) + 64 (temporal channels) = 128
        self.fusion_network = nn.Sequential(
            nn.Linear(in_features=128 * 64, out_features=256),
            nn.SiLU(),
            nn.Dropout(p=0.1),
            nn.Linear(in_features=256, out_features=latent_dim),
            nn.LayerNorm(latent_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Executes forward processing loop over incoming batch tensors.

        Expected Input Shape: (Batch_Size, 4, 1280)
        """
        if x.dtype != torch.float32:
            x = x.to(torch.float32)

        # Deconstruct the input matrix asymmetry cleanly
        # Rows 0 & 3 -> Spectral. Rows 1 & 2 -> Temporal.
        spectral_inputs = torch.cat([x[:, 0:1, :], x[:, 3:4, :]], dim=1)
        temporal_inputs = x[:, 1:3, :]

        # Extract features through domain-isolated convolutional layers
        spec_feats = self.spectral_conv(spectral_inputs)
        temp_feats = self.temporal_conv(temporal_inputs)

        # Flatten and fuse into high-dimensional vector space
        spec_flat = spec_feats.view(spec_feats.size(0), -1)
        temp_flat = temp_feats.view(temp_feats.size(0), -1)

        combined = torch.cat([spec_flat, temp_flat], dim=1)
        latent_vector = self.fusion_network(combined)

        return latent_vector


if __name__ == "__main__":
    print("[INIT] Verifying PyTorch Asymmetric Spatial Encoder architecture...")
    model = AsymmetricSpatialEncoder(latent_dim=128)
    model.eval()

    # Simulate an incoming batch of 4 pipelines to test dimensionality bounds
    mock_batch = torch.randn(4, 4, 1280)
    with torch.no_grad():
        output_tokens = model(mock_batch)

    print(f" -> Simulated Input Ingestion Shape: {mock_batch.shape}")
    print(f" -> Compiled Latent Output Shape   : {output_tokens.shape}")

    assert output_tokens.shape == (4, 128), "Error: Latent dimensional variance detected."
    print("[SUCCESS] PyTorch Neural Network architecture verified for deployment.")
