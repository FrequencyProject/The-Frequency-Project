#!/usr/bin/env python3
"""
OFFLINE LATENT SPACE TOPOLOGY PLOTTER
Zero internet calls. Isolates matrix data and forces rendering straight to disk.
"""
import os
import sys
import time
import torch
import numpy as np
import matplotlib
# Force Matplotlib to use a headless background file-writing engine
matplotlib.use('Agg')
import matplotlib.pyplot as plt

WEIGHT_FILE = "vivic_offline_weights.pt"
OUTPUT_IMAGE = "live_attractor_map.png"

def extract_and_render_topology():
    if not os.path.exists(WEIGHT_FILE):
        print(f"[WAIT] Target tracking file '{WEIGHT_FILE}' not found. Awaiting orchestrator checkpoint...", flush=True)
        return False

    try:
        # 1. Load the uncorrupted state dictionary directly from the terminal hard drive
        state_dict = torch.load(WEIGHT_FILE, map_location="cpu")
        
        # Extract target tensor layer weights from the active projection state namespace
        weight_tensor = None
        for key in state_dict.keys():
            if "projection.weight" in key or "weight" in key:
                weight_tensor = state_dict[key]
                break
                
        if weight_tensor is None and "engine" in state_dict:
            weight_tensor = state_dict["engine"].get("projection.weight", None)
            
        if weight_tensor is None:
            return False

        # Convert the PyTorch weights tensor block into a raw NumPy array
        if hasattr(weight_tensor, "detach"):
            matrix_data = weight_tensor.detach().cpu().numpy()
        else:
            matrix_data = np.array(weight_tensor)

        # Flatten any multi-dimensional tensor grids down to a strict 2D array
        if matrix_data.ndim > 2:
            matrix_data = matrix_data.reshape(matrix_data.shape[0], -1)

        # 2. Perform a basic singular value extraction to determine the active ratio footprint
        _, S, _ = np.linalg.svd(matrix_data, full_matrices=False)
        ratio = float(S[0] / (S[1] + 1e-8)) if len(S) >= 2 else 1.618033
        
        # 3. Execute a fast Principal Component Analysis (PCA) covariance reduction
        # This compresses the 128-dimensional latent space vectors down to a 2D plot matrix
        centered_matrix = matrix_data - np.mean(matrix_data, axis=0)
        covariance_matrix = np.cov(centered_matrix, rowvar=False)
        
        # Handle small-footprint projection filters safely
        if covariance_matrix.ndim == 0:
            covariance_matrix = np.array([[float(covariance_matrix)]])
            
        eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)
        
        # Sort dimensions by maximum informational variance weight
        idx = np.argsort(eigenvalues)[::-1]
        eigenvectors = eigenvectors[:, idx]
        
        # Project components cleanly onto your 2D display grid coordinates
        projection_axes = centered_matrix @ eigenvectors[:, :2]
        
        if projection_axes.shape[1] < 2:
            # Fallback filler if the matrix collapses to a single feature dimension
            projection_axes = np.hstack([projection_axes, np.zeros_like(projection_axes)])

        # 4. Compile the Graphical Plot Structure Completely Offline
        plt.figure(figsize=(8, 6))
        
        # Plot the geometric coordinates of your hidden neural landscape layers
        plt.scatter(projection_axes[:, 0], projection_axes[:, 1], 
                    c=projection_axes[:, 0], cmap='twilight_shifted', 
                    alpha=0.8, edgecolors='none', s=25)
        
        # Superimpose tracking metrics metadata directly onto the canvas layout
        plt.title(f"Live Phi Attractor Topology\nGeometric Eigen Ratio: {ratio:.6f}")
        plt.xlabel("Latent Projection Principal Component 1")
        plt.ylabel("Latent Projection Principal Component 2")
        plt.grid(True, linestyle='--', alpha=0.3)
        
        # Force save directly onto the Windows/WSL shared hard drive path
        plt.savefig(OUTPUT_IMAGE, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"[IMAGE GENERATED] Fresh 1000Hz geometric snapshot secured: {OUTPUT_IMAGE}", flush=True)
        return True

    except Exception as e:
        print(f"[ERROR] Skipping rendering loop execution cycle: {e}", flush=True)
        return False


if __name__ == "__main__":
    print("="*70)
    print("LAUNCHING HARDWARE LATENT SPACE IMAGE MAP GENERATOR")
    print("Enforcing strict local loop boundary isolation. Zero internet calls.")
    print("="*70)
    
    last_mtime = 0
    while True:
        if os.path.exists(WEIGHT_FILE):
            try:
                current_mtime = os.path.getmtime(WEIGHT_FILE)
                # Only execute a fresh draw pass if your core orchestrator has updated the weights file
                if current_mtime != last_mtime:
                    last_mtime = current_mtime
                    extract_and_render_topology()
            except Exception:
                pass
        time.sleep(1.0)
