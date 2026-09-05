#!/usr/bin/env python3
"""Phase 4: 1D-CNN Spatial Encoder Model Architecture.

Validates input tensor shapes for single-stream and batched telemetry vectors, 
applying standard feature extraction and precision type-casting.
"""
import torch
import torch.nn as nn

class AsymmetricSpatialEncoder(nn.Module):
    """Convolutional neural network for feature extraction and latent mapping."""

    def __init__(self, latent_dim: int = 128):
        super().__init__()
        self.latent_dim = latent_dim
        
        # 1D Convolutional layers targeting the 4 input channels
        self.feature_extractor = nn.Sequential(
            nn.Conv1d(in_channels=4, out_channels=16, kernel_size=15, stride=2, padding=7),
            nn.BatchNorm1d(16),
            nn.ReLU(),
            nn.Conv1d(in_channels=16, out_channels=32, kernel_size=7, stride=2, padding=3),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(4)  # Reduces sequence length safely down to a fixed spatial anchor
        )
        
        # Linear layers mapping down to the target latent dimensions
        self.fc = nn.Sequential(
            nn.Linear(32 * 4, latent_dim),
            nn.LayerNorm(latent_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Executes the forward inference pass while validating input tensor dimensions.

        Args:
            x: An incoming float32 tensor representing the multi-channel waveform matrix.
               Expected shapes: Unbatched (4, 1280) or Batched (N, 4, 1280).

        Returns:
            A latent feature tensor of shape (N, latent_dim).
        """
        # Validate input type and structural geometry shapes
        if not isinstance(x, torch.Tensor):
            raise TypeError(f"Model Input Firewall: Expected torch.Tensor instance, received {type(x)}.")

        shape_dims = x.shape

        # Case A: Handle single-stream, unbatched signals (4, 1280)
        if len(shape_dims) == 2:
            if shape_dims[0] != 4:
                raise ValueError(f"Model Input Firewall: Unbatched stream requires exactly 4 tracks. Received {shape_dims[0]}.")
            if shape_dims[1] != 1280:
                raise ValueError(f"Model Input Firewall: Unbatched sequence requires exactly 1280 steps. Received {shape_dims[1]}.")
            
            # Dynamically expand dimension to create an active batch size of 1
            x = x.unsqueeze(0)

        # Case B: Handle batched processing blocks (N, 4, 1280)
        elif len(shape_dims) == 3:
            if shape_dims[1] != 4:
                raise ValueError(f"Model Input Firewall: Batched tensor track dimension must equal 4. Received {shape_dims[1]}.")
            if shape_dims[2] != 1280:
                raise ValueError(f"Model Input Firewall: Batched tensor sequence dimension must equal 1280. Received {shape_dims[2]}.")
        
        # Case C: Reject unsupported multidimensional anomalies instantly
        else:
            raise ValueError(f"Model Input Firewall: Invalid dimension configuration. Expected 2D or 3D tensor, received shape {shape_dims}.")

        # Force single-precision casting to normalize types before network operations
        x = x.float()

        # Execute 1D convolutional feature extraction layers
        features = self.feature_extractor(x)
        
        # Flatten spatial feature rows cleanly into vectors
        flattened = features.view(features.size(0), -1)
        
        # Map features onto the standard latent spaces layer
        latent_vector = self.fc(flattened)
        return latent_vector
