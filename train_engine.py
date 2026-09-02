#!/usr/bin/env python3
"""Phase 4: Integrated Neural Network Optimization and Backpropagation Engine.

Coordinates raw tensor mappings, optimization updates, and forward-backward training steps.
[PROTECTED BY AN INTEGRATED INFRASTRUCTURE ENCLOSURE MANDATE]
"""
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from model_architecture import AsymmetricSpatialEncoder
from resonance_loss import ResonanceCoherenceLoss
from sensor_adapter import MultiChannelSensorAdapter

class VivicTrainingEngine:
    """Manages weights, gradient tracking states, and micro-batch training steps."""

    def __init__(self, port: str = "MOCK"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = AsymmetricSpatialEncoder().to(self.device)
        self.criterion = ResonanceCoherenceLoss()
        self.optimizer = optim.AdamW(self.model.parameters(), lr=1e-3, weight_decay=1e-4)
        
        # Internal reference adapter tracking input ingestion
        self.adapter = MultiChannelSensorAdapter(port=port)
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
        features = self.adapter.get_ai_features()
        
        # Verify buffer warm-up behavior safely
        if np.all(features == 0.0):
            return -1.0, None
            
        self.warmed_up = True
        
        # 2. BACKWARDS-COMPATIBILITY GUARD: Fallback to neutral arrays if arguments are omitted in tests
        if ambient_means is None:
            ambient_means = np.zeros(4, dtype=np.float32)
        if ambient_stds is None:
            ambient_stds = np.ones(4, dtype=np.float32)
        
        # 3. Apply environmental baseline noise calibration adjustments natively on the input matrix
        for ch in range(4):
            if ambient_stds[ch] > 1e-6:
                features[ch] = (features[ch] - ambient_means[ch]) / ambient_stds[ch]

        # 4. P1 FINITE-VALUE FIREWALL: Instant check for NaNs or non-finite elements
        if not np.all(np.isfinite(features)):
            print("[SECURITY QUARANTINE] Non-finite values detected in ingestion matrix. Squashing frame.")
            return -1.0, None

        # 5. Pack normalized footprint array cleanly into single-precision execution tensors
        torch_tensor = torch.from_numpy(features).unsqueeze(0).float().to(self.device)
        
        if not torch.all(torch.isfinite(torch_tensor)):
            return -1.0, None

        # 6. Clear accumulated gradient registers
        self.optimizer.zero_grad()

        # 7. Execute forward pass—generating the latent vector representation
        latent_vector = self.model(torch_tensor)

        # 8. Evaluate mathematical loss using resonance coherence channels
        loss = self.criterion(latent_vector)

        # 9. Trigger backpropagation pass and update model parameter layers
        loss.backward()
        
        # Apply strict gradient clipping to insulate weights against gradient explosions
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
        
        self.optimizer.step()

        # P1 OPTIMIZATION: Return the loss along with the already calculated latent vector
        return loss.item(), latent_vector
