#!/usr/bin/env python3
"""Phase 4: 1D-CNN Asymmetric Spatial Encoder Model Architecture.

Enforces strict input dimension contracts and structural tensor shape perimeters 
for single-stream waveforms and parallel execution profiles with automatic precision casting.
"""
import torch
import torch.nn as nn

class AsymmetricSpatialEncoder(nn.Module):
    """Deep learning feature extraction network with embedded dimension firewalls."""

    def __init__(self, latent_dim: int = 128):
        super().__init__()
        self.latent_dim = latent_dim
        
        # 1D Convolutional feature extractors targeting 4 physical telemetry tracks
        self.feature_extractor = nn.Sequential(
            nn.Conv1d(in_channels=4, out_channels=16, kernel_size=15, stride=2, padding=7),
            nn.BatchNorm1d(16),
            nn.ReLU(),
            nn.Conv1d(in_channels=16, out_channels=32, kernel_size=7, stride=2, padding=3),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(4)  # Reduces sequence length safely down to a fixed spatial anchor
        )
        
        # Linear layer mapping down to the high-dimensional latent space representation
        self.fc = nn.Sequential(
            nn.Linear(32 * 4, latent_dim),
            nn.LayerNorm(latent_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Executes the forward inference pass while validating shape perimeters.

        Args:
            x: An incoming float32 tensor representing the multi-channel waveform matrix.
               Expected shapes: Unbatched (4, 1280) or Batched (N, 4, 1280).

        Returns:
            A clean, bounded latent feature tensor of shape (N, latent_dim).
        """
        # 1. HARDENING REMEDIATION: Frontline Input Shape Contract Validation
        if not isinstance(x, torch.Tensor):
            raise TypeError(f"Model Input Firewall: Expected torch.Tensor instance, received {type(x)}.")

        shape_dims = x.shape

        # Case A: Handle Single-Stream, Unbatched Waves (4, 1280) Natively
        if len(shape_dims) == 2:
            if shape_dims[0] != 4:
                raise ValueError(f"Model Input Firewall: Unbatched stream requires exactly 4 tracks. Received {shape_dims[0]}.")
            if shape_dims[1] != 1280:
                raise ValueError(f"Model Input Firewall: Unbatched sequence requires exactly 1280 windows. Received {shape_dims[1]}.")
            
            # Dynamically unsqueeze to inject an active batch dimension of 1 for execution stability
            x = x.unsqueeze(0)

        # Case B: Handle Multidimensional Parallel Execution Batches (N, 4, 1280)
        elif len(shape_dims) == 3:
            if shape_dims[1] != 4:
                raise ValueError(f"Model Input Firewall: Batched tensor track dimension must equal 4. Received {shape_dims[1]}.")
            if shape_dims[2] != 1280:
                raise ValueError(f"Model Input Firewall: Batched tensor sequence dimension must equal 1280. Received {shape_dims[2]}.")
        
        # Case C: Reject un-supported multidimensional anomalies instantly
        else:
            raise ValueError(f"Model Input Firewall: Invalid tensor dimension matrix configuration. Expected 2D or 3D tensor, received shape {shape_dims}.")

        # HARDENING REMEDIATION: Enforce an absolute single-precision casting (.float()) 
        # checkpoint to convert double-precision types (float64) seamlessly before tensor operations.
        x = x.float()

        # 2. Execute deep convolutional feature extraction loops safely
        features = self.feature_extractor(x)
        
        # Flatten spatial tracks cleanly down to complete the mapping matrix
        flattened = features.view(features.size(0), -1)
        
        # 3. Output standard single-precision high-dimensional latent vector arrays
        latent_vector = self.fc(flattened)
        return latent_vector
