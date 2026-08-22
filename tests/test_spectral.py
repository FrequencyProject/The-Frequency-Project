import numpy as np
from spectral_processing import AsymmetricTensorPipeline


def test_dimensions():
    p = AsymmetricTensorPipeline()
    assert p.compile_feature_tensor(
        np.zeros(2560), np.zeros(1280), np.zeros(1280), np.zeros(2560)
    ).shape == (4, 1280)
