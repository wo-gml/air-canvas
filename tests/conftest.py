import numpy as np
import pytest


@pytest.fixture
def frame() -> np.ndarray:
    """640x480 검은 프레임."""
    return np.zeros((480, 640, 3), dtype=np.uint8)
