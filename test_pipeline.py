import sys
import numpy as np
from prototype_simulation import execute_ecological_ingestion_pipeline

def verify_canonical_pipeline_constraints():
    """
    Executes local structural, dimensional, and value-boundary 
    assertions against the canonical execution module.
    """
    print("[TEST] Running local pipeline synchronization checks...")
    
    # Ingest the unified tensor using the canonical parameters
    tensor = execute_ecological_ingestion_pipeline(seed=42)
    
    # Assert the rigid 3x1280 matrix shape defined in the project blueprint
    assert tensor.shape == (3, 1280), f"Dimensional mismatch: Expected (3, 1280), got {tensor.shape}"
    
    # Validate that min-max normalization forces values precisely within [0, 1]
    assert np.min(tensor) >= 0.0, "Boundary violation: Normalized data floor dropped below 0.0"
    assert np.max(tensor) <= 1.0, "Boundary violation: Normalized data ceiling exceeded 1.0"
    
    print("[TEST] All local file assertions verified successfully.")
    return tensor

if __name__ == "__main__":
    matrix = verify_canonical_pipeline_constraints()
    
    # Run truncated matrix view if debug flag is explicitly passed
    if "--debug" in sys.argv:
        print(f"[TEST] Clean array slice evaluation:\n{matrix[:, :4]}")
