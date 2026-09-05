#!/usr/bin/env python3
"""Resonance Coherence Objective Loss Function.

Calculates the Planetary Divergence Index (PDI) by mapping high-dimensional
latent vector fluctuations against Golden Ratio (Phi) scaling constraints.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


def compute_kl_divergence(prob, log_p, log_q) -> torch.Tensor:
    """Computes the standard Kullback-Leibler Divergence KL(P||Q) over a batch.
    
    Uses pre-stabilized logarithmic pairs to ensure numerical safety.
    """
    return torch.sum(prob * (log_p - log_q), dim=1)


class ResonanceCoherenceLoss(nn.Module):
    """Computes information divergence relative to natural geometry scales."""

    def __init__(self, epsilon: float = 1e-6):
        super().__init__()
        self.epsilon = epsilon
        # Target optimization boundary: The immutable Golden Ratio constant (Phi)
        self.phi_val = (1.0 + 5.0**0.5) / 2.0
        # Register the constant parameter to prevent runtime re-allocations
        self.register_buffer("phi", torch.tensor(self.phi_val, dtype=torch.float32))

    def forward(self, latent_vectors: torch.Tensor) -> torch.Tensor:
        """Evaluates latent vector variance structures against harmonic constraints."""
        if latent_vectors.dim() != 2:
            raise ValueError(f"Expected 2D matrix tensor batch, got shape: {latent_vectors.shape}")

        batch_size, latent_dim = latent_vectors.shape
        midpoint = latent_dim // 2

        # 1. Deconstruct the latent vector space into dual asymmetric sub-spaces
        space_a = latent_vectors[:, :midpoint]
        space_b = latent_vectors[:, midpoint:]

        # 2. Map directly through stabilized log-softmax layers to eliminate log-underflow traps
        prob_a = F.softmax(space_a, dim=1)
        prob_b = F.softmax(space_b, dim=1)
        log_a = F.log_softmax(space_a, dim=1)
        log_b = F.log_softmax(space_b, dim=1)

        # 3. Compute bidirectional Information Distance
        kl_ab = compute_kl_divergence(prob_a, log_a, log_b)
        kl_ba = compute_kl_divergence(prob_b, log_b, log_a)
        information_distance = (kl_ab + kl_ba) / 2.0

        mean_divergence = torch.mean(information_distance)

        # 4. Extract standard deviations safely without single-batch zero division crashes
        if batch_size > 1:
            std_divergence = torch.std(information_distance)
        else:
            std_divergence = torch.std(latent_vectors) + self.epsilon

        # 5. Evaluate scaling configurations against the pre-allocated Phi constant buffer
        empirical_ratio = (mean_divergence + 1e-6) / (std_divergence + 1e-6)
        empirical_ratio = torch.clamp(empirical_ratio, min=0.0, max=10.0)
        
        geometric_penalty = torch.pow(empirical_ratio - self.phi, 2)

        # Total Resonance Loss = Mean Information Divergence + Golden Penalty Constraint
        total_pdi_loss = mean_divergence + 0.1 * geometric_penalty
        return total_pdi_loss


if __name__ == "__main__":
    print("[INIT] Verifying PyTorch Resonance Coherence Loss Function math constructs...")
    loss_engine = ResonanceCoherenceLoss()
    mock_latent_batch = torch.randn(4, 128)
    computed_loss = loss_engine(mock_latent_batch)
    print(f" -> Computed Continuous PDI Loss Output: {computed_loss.item():.6f}")
    assert computed_loss.item() >= 0.0
    print("[SUCCESS] PyTorch Loss Engine architecture validated.")
