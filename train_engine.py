#!/usr/bin/env python3
"""Phase 4: Integrated Neural Network Optimization and Backpropagation Engine.

Coordinates raw tensor mappings, optimization updates, and forward-backward training steps.
Decoupled architectural engine supporting strict dependency injection contracts.
"""
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from model_architecture import AsymmetricSpatialEncoder
from resonance_loss import ResonanceCoherenceLoss
from sensor_adapter import MultiChannelSensorAdapter


class TelemetryPreprocessor:
    """Handles environmental baseline noise calibration corrections and input sanitization."""

    @staticmethod
    def calibrate_and_verify(features: np.ndarray, ambient_means: np.ndarray = None, ambient_stds: np.ndarray = None) -> np.ndarray:
        """Applies dynamic baseline corrections and tests array elements for stability."""
        if ambient_means is None:
            ambient_means = np.zeros(4, dtype=np.float32)
        if ambient_stds is None:
            ambient_stds = np.ones(4, dtype=np.float32)

        # Apply environmental baseline noise calibration adjustments natively on the input matrix
        corrected_features = features.copy()
        for ch in range(4):
            if ambient_stds[ch] > 1e-6:
                corrected_features[ch] = (corrected_features[ch] - ambient_means[ch]) / ambient_stds[ch]

        if not np.all(np.isfinite(corrected_features)):
            print("[SECURITY QUARANTINE] Non-finite values detected in ingestion matrix. Squashing frame.")
            return None

        return corrected_features


class VivicTrainingEngine:
    """Manages weights, gradient tracking states, and micro-batch training steps via dependency injection."""

    def __init__(self, model: nn.Module = None, criterion: nn.Module = None, optimizer: optim.Optimizer = None, adapter: MultiChannelSensorAdapter = None, *args, **kwargs):
        """Initializes optimization loops, absorbing extra configuration keyword arguments gracefully."""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Dependency Injection Layer with smart production fallbacks
        self.model = model.to(self.device) if model is not None else AsymmetricSpatialEncoder().to(self.device)
        self.criterion = criterion if criterion is not None else ResonanceCoherenceLoss()

        if optimizer is not None:
            self.optimizer = optimizer
        else:
            self.optimizer = optim.AdamW(self.model.parameters(), lr=1e-3, weight_decay=1e-4)

        # P1 DECOUPLING: Absorbs 'port' configuration passthroughs if supplied via orchestrators or tests
        if adapter is not None:
            self.adapter = adapter
        else:
            port_param = kwargs.get("port", "MOCK")
            self.adapter = MultiChannelSensorAdapter(port=port_param)

        self.preprocessor = TelemetryPreprocessor()
        self.warmed_up = False

    def train_step(self, ambient_means: np.ndarray = None, ambient_stds: np.ndarray = None) -> tuple:
        """Executes a single high-performance forward-backward parameter adjustment optimization pass.

        Args:
            ambient_means (np.ndarray, optional): Dynamic baseline noise calibration means. Defaults to None.
            ambient_stds (np.ndarray, optional): Dynamic baseline noise calibration standard deviations. Defaults to None.

        Returns:
            tuple: (loss_scalar, latent_vector_tensor) or (-1.0, None) on buffer starvation.
        """
        self.model.train()

        # 1. Fetch raw multi-channel feature frames from the ingestion layer
        raw_features = self.adapter.get_ai_features().copy()

        # Verify buffer warm-up behavior safely
        if np.all(raw_features == 0.0):
            return -1.0, None

        # 2. Delegate environmental baseline calibration and validation checks to the preprocessor class
        features = self.preprocessor.calibrate_and_verify(raw_features, ambient_means, ambient_stds)
        if features is None:
            return -1.0, None

        self.warmed_up = True

        # 3. Instantiate device-native tensor block cleanly
        torch_tensor = torch.tensor(features, dtype=torch.float32, device=self.device).unsqueeze(0)
        if not torch.all(torch.isfinite(torch_tensor)):
            return -1.0, None

        # 4. Clear accumulated gradient registers before forward pass
        self.optimizer.zero_grad()

        # 5. Execute forward pass—generating the latent vector representation
        latent_vector = self.model(torch_tensor)

        # 6. Evaluate mathematical loss using resonance coherence channels
        loss = self.criterion(latent_vector)

        # 7. Trigger backpropagation pass to populate raw gradients
        loss.backward()

        # 8. Gradient norm clipping boundary check
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)

        # 9. Execute the optimizer step safely
        self.optimizer.step()

        # 10. Graph detachment isolation protecting context loops against leaks
        safe_latent_vector = latent_vector.detach()

        return loss.item(), safe_latent_vector
