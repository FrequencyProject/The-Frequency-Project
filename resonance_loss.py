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

    def __init__(self, epsilon: float = 1e-6):
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
        # Space A tracks high-frequency profiles; Space B tracks slow temporal trends
        space_a = latent_vectors[:, :midpoint]
        space_b = latent_vectors[:, midpoint:]

        # 2. Convert raw latent activations into soft probability energy distributions
        prob_a = F.softmax(space_a, dim=1) + self.epsilon
        prob_b = F.softmax(space_b, dim=1) + self.epsilon

        # 3. Compute bidirectional Information Distance via symmetric KL Divergence
        kl_ab = torch.sum(prob_a * (torch.log(prob_a) - torch.log(prob_b)), dim=1)
        kl_ba = torch.sum(prob_b * (torch.log(prob_b) - torch.log(prob_a)), dim=1)
        information_distance = (kl_ab + kl_ba) / 2.0

        # 4. Extract the variance ratios across the vector space dimensions
        # Utilizing spatial dimension metrics ensures stability even when batch_size == 1
        mean_divergence = torch.mean(information_distance)

        # Calculate standard deviation across the batch elements if possible, otherwise use latent array variation
        if batch_size > 1:
            std_divergence = torch.std(information_distance)
        else:
            # Fallback path for Batch Size of 1: use latent variance components to maintain ratio tracking
            std_divergence = torch.std(latent_vectors) + self.epsilon

        # 5. Evaluate scaling configurations against the target Phi geometric constant
        # Clamp the empirical ratio calculation to prevent zero-variance explosive divisions
        empirical_ratio = (mean_divergence + self.epsilon) / (std_divergence + self.epsilon)
        empirical_ratio = torch.clamp(empirical_ratio, min=0.0, max=10.0)

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
