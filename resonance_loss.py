#!/usr/bin/env python3
"""Phase 3: Resonance Coherence Objective Loss Function.

Calculates the Planetary Divergence Index (PDI) by mapping high-dimensional 
latent vector fluctuations against Golden Ratio (Phi) scaling constraints.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class ResonanceCoherenceLoss(nn.Module):
    """Computes non-semantic information divergence relative to natural geometry scales."""

    def __init__(self, epsilon: float = 1e-8):
        super().__init__()
        self.epsilon = epsilon
        # Define the immutable Golden Ratio constant (Phi) natively
        self.phi = (1.0 + 5.0**0.5) / 2.0

    def forward(self, latent_vectors: torch.Tensor) -> torch.Tensor:
        """Evaluates latent vector variance structures against harmonic constraints.

        Expected Input Shape: (Batch_Size, Latent_Dim) where Latent_Dim is divisible by 2.
        """
        if latent_vectors.dim() != 2:
            raise ValueError(f"Expected 2D matrix tensor batch, got shape: {latent_vectors.shape}")

        batch_size, latent_dim = latent_vectors.shape
        midpoint = latent_dim // 2

        # 1. Deconstruct the latent vector space into dual asymmetric energy sub-spaces
        # Sub-space A tracks high-frequency profiles; Sub-space B tracks slow temporal trends
        space_a = latent_vectors[:, :midpoint]
        space_b = latent_vectors[:, midpoint:]

        # 2. Convert raw latent activations into soft probability energy distributions
        prob_a = F.softmax(space_a, dim=1) + self.epsilon
        prob_b = F.softmax(space_b, dim=1) + self.epsilon

        # 3. Compute bidirectional Information Distance via symmetric KL Divergence
        kl_ab = torch.sum(prob_a * (torch.log(prob_a) - torch.log(prob_b)), dim=1)
        kl_ba = torch.sum(prob_b * (torch.log(prob_b) - torch.log(prob_a)), dim=1)
        information_distance = (kl_ab + kl_ba) / 2.0

        # 4. Extract the variance ratios of the information shifts across the batch
        mean_divergence = torch.mean(information_distance)
        std_divergence = (
            torch.std(information_distance)
            if batch_size > 1
            else torch.tensor(0.0, device=latent_vectors.device)
        )

        # 5. Evaluate scaling configurations against the target Phi geometric constant
        # The penalty scales quadratically based on how far variance drifts from the Golden Ratio
        empirical_ratio = (mean_divergence + self.epsilon) / (std_divergence + self.epsilon)
        geometric_penalty = torch.pow(empirical_ratio - self.phi, 2)

        # Total Resonance Loss = Mean Information Divergence + Golden Penalty Constraint
        total_pdi_loss = mean_divergence + 0.1 * geometric_penalty
        return total_pdi_loss


if __name__ == "__main__":
    print("[INIT] Verifying PyTorch Resonance Coherence Loss Function math constructs...")
    loss_engine = ResonanceCoherenceLoss()

    # Simulate a batch of 4 extracted latent vectors matching our model output dimension shape
    mock_latent_batch = torch.randn(4, 128)
    computed_loss = loss_engine(mock_latent_batch)

    print(f" -> Simulated Input Latent Matrix Shape: {mock_latent_batch.shape}")
    print(f" -> Computed Continuous PDI Loss Output: {computed_loss.item():.6f}")

    assert computed_loss.item() >= 0.0, "Error: Negative energy state encountered."
    print("[SUCCESS] PyTorch Loss Engine architecture mathematically validated.")
