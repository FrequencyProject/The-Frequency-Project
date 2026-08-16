import sys
import numpy as np
from prototype_simulation import execute_ecological_ingestion_pipeline

def run_local_pipeline_assertions():
    """
    Executes structural and mathematical validation checks 
    against the canonical execution pipeline.
    """
    print("[TEST] Initializing canonical verification hooks...")
    tensor = execute_ecological_ingestion_pipeline(seed=42)
    
    # Assert exact matrix bounds required by the project specifications
    assert tensor.shape == (3, 1280), f"Structural error: Expected (3, 1280), got {tensor.shape}"
    assert np.min(tensor) >= 0.0, "Mathematical error: Tensor values dropped below normalized 0.0 floor"
    assert np.max(tensor) <= 1.0, "Mathematical error: Tensor values exceeded normalized 1.0 ceiling"
    
    print("[TEST] All local pipeline assertions passed successfully.")
    return tensor

if __name__ == "__main__":
    matrix = run_local_pipeline_assertions()
    
    # Keep local debugging terminal outputs silent unless explicitly requested
    if "--debug" in sys.argv:
        print(f"[TEST] Matrix verification slice:\n{matrix[:, :3]}")
