import pytest
import numpy as np
from crypto_signer import HardwareTelemetrySigner

def test_crypto_signer_tuple_and_array_compatibility():
    """Validates that the secure signer smoothly processes both arrays and native streaming tuples."""
    signer = HardwareTelemetrySigner(use_simulation=True)
    
    test_tuple = (0.1122, -0.3344, 0.5566, -0.7788)
    test_array = np.array(test_tuple, dtype=np.float32)
    
    # 1. Process ingestion tuple
    p1, s1 = signer.sign_vector(test_tuple)
    # 2. Process array matrix
    p2, s2 = signer.sign_vector(test_array)
    
    assert p1 == p2, "Data mismatch: Data binary footprints drifted between array and tuple blocks."
    assert s1 == s2, "Signature mismatch: Cryptographic hashes drifted between input types."
    assert signer.verify_vector_signature(p1, s1) is True

def test_crypto_signer_malformed_input_rejection():
    """Ensures out-of-bounds dimensions trigger immediate type/value errors at the perimeter gate."""
    signer = HardwareTelemetrySigner(use_simulation=True)
    
    # Malformed tuple size (3 elements instead of 4)
    with pytest.raises(ValueError, match="Cryptographic signer requires a verified 4-element telemetry structure."):
        signer.sign_vector((1.0, 2.0, 3.0))
        
    # Unsupported data type injection format
    with pytest.raises(TypeError, match="Unsupported payload data structure passed to secure signing interface."):
        signer.sign_vector("INVALID_STRING_RAW_DATA_STREAM")
