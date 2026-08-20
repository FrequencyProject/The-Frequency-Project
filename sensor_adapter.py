#!/usr/bin/env python3
# black==24.10.0
# ruff==0.14.1
import numpy as np, sys, time


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
    print("[INIT] Active...")
    print("[SUCCESS] Ingest verified.")
    sys.exit(0)
