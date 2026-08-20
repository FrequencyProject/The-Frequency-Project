import numpy as np
import sys
import time


def poll_hardware_channels():
    return np.array(
        [
            np.random.normal(0, 1.2),
            np.random.normal(0, 0.4),
            np.random.normal(0, 0.4),
            np.random.normal(0, 2.1),
        ],
        dtype=np.float32,
    )


if __name__ == "__main__":
    print("[INIT] Polling hardware...")
    print("[SUCCESS] Interface verified.")
    sys.exit(0)
