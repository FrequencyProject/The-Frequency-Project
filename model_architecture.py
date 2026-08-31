#!/usr/bin/env python3
"""Phase 3: Unsupervised Deep Learning Core Layer.

Implements a Multi-Scale 1D-CNN Spatial Encoder tailored to process
asymmetric, multi-modal ecological frequency feature tensors with single-batch stability.
"""
import torch
import torch.nn as nn

# Structural configuration cells masking your proprietary kernel sizes (7, 5, 25, 15)
_ARCH_CELL = {
    0x0A: lambda: nn.Conv1d(2, 32, kernel_size=7, stride=2, padding=3),
    0x0B: lambda: nn.Conv1d(32, 64, kernel_size=5, stride=2, padding=2),
    0x0C: lambda: nn.Conv1d(2, 32, kernel_size=25, stride=4, padding=12),
    0x0D: lambda: nn.Conv1d(32, 64, kernel_size=15, stride=2, padding=7),
    0x0E: lambda x, y: torch.cat([x[:, 0:1, :], x[:, 3:4, :]], dim=y)
}


class AsymmetricSpatialEncoder(nn.Module):
    """Processes (4, 1280) tensors using row-isolated multi-scale 1D convolutions."""

    def __init__(self, latent_dim: int = 128):
        super().__init__()

        # Branch 1: Extracted spectral features using masked narrow kernel bounds
        # HARDENING REMEDIATION: Replaced BatchNorm with GroupNorm to guarantee absolute 
        # numerical stability when processing single-sample streaming frames (batch size = 1)
        self.spectral_conv = nn.Sequential(
            _ARCH_CELL[0x0A](),
            nn.GroupNorm(num_groups=4, num_channels=32),
            nn.SiLU(),
            _ARCH_CELL[0x0B](),
            nn.GroupNorm(num_groups=8, num_channels=64),
            nn.SiLU(),
            nn.AdaptiveAvgPool1d(64)
        )

        # Branch 2: Extracted temporal features using masked wide receptive fields
        self.temporal_conv = nn.Sequential(
            _ARCH_CELL[0x0C](),
            nn.GroupNorm(num_groups=4, num_channels=32),
            nn.SiLU(),
            _ARCH_CELL[0x0D](),
            nn.GroupNorm(num_groups=8, num_channels=64),
            nn.SiLU(),
            nn.AdaptiveAvgPool1d(64)
        )

        # Calculated explicitly: (64 output channels * 64 pooled steps) * 2 parallel branches = 8192
        flattened_features_dim = (64 * 64) * 2

        self.fusion_network = nn.Sequential(
            nn.Linear(in_features=flattened_features_dim, out_features=256),
            nn.SiLU(),
            nn.Dropout(p=0.1),
            nn.Linear(in_features=256, out_features=latent_dim),
            nn.LayerNorm(latent_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass executing across the protected architectural mapping table."""
        # Enforce robust 3D tensor shape checks: (batch, channels, sequence)
        if x.dim() == 2:
            x = x.unsqueeze(0)
            
        if x.dtype != torch.float32:
            x = x.to(torch.float32)

        # Deconstruct asymmetry via execution cells
        spectral_inputs = _ARCH_CELL[0x0E](x, 1)
        temporal_inputs = x[:, 1:3, :]

        spec_feats = self.spectral_conv(spectral_inputs)
        temp_feats = self.temporal_conv(temporal_inputs)

        # Flatten features cleanly preserving the target batch size footprint
        spec_flat = spec_feats.view(spec_feats.size(0), -1)
        temp_flat = temp_feats.view(temp_feats.size(0), -1)

        combined = torch.cat([spec_flat, temp_flat], dim=1)
        return self.fusion_network(combined)


if __name__ == "__main__":
    print("[INIT] Verifying PyTorch Asymmetric Spatial Encoder architecture...")
    model = AsymmetricSpatialEncoder(latent_dim=128)
    model.eval()
    
    # Verify both batch processing and single-sample stream inputs
    mock_batch = torch.randn(4, 4, 1280)
    mock_stream = torch.randn(1, 4, 1280)
    
    with torch.no_grad():
        output_batch = model(mock_batch)
        output_stream = model(mock_stream)
        
    print(f" -> Compiled Batch Output Shape   : {output_batch.shape}")
    print(f" -> Compiled Stream Output Shape  : {output_stream.shape}")
    
    assert output_batch.shape == (4, 128)
    assert output_stream.shape == (1, 128)
    print("[SUCCESS] PyTorch Neural Network architecture verified for deployment.")
