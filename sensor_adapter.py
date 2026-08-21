#!/usr/bin/env python3
import collections

import numpy as np


class MultiChannelSensorAdapter:
    """4-channel ingestion adapter for compiling a normalized AI tensor window."""

    def __init__(self, port: str, baudrate: int, window_size: int = 1280) -> None:
        self.port = port
        self.baudrate = baudrate
        self.window_size = window_size
        self.num_channels = 4
        self.channels = [collections.deque(maxlen=window_size) for _ in range(self.num_channels)]

    def process_incoming_packet(self, packet_str: str) -> None:
        """Parse packet strings and append valid 4-channel values to rolling buffers."""
        try:
            pairs = packet_str.strip().split(",")
            if len(pairs) != self.num_channels:
                return

            parsed_values: dict[str, float] = {}
            for pair in pairs:
                key, val_str = pair.split(":")
                parsed_values[key] = float(val_str)

            ordered_values = [parsed_values[f"V{i + 1}"] for i in range(self.num_channels)]
            for i in range(self.num_channels):
                self.channels[i].append(ordered_values[i])
        except (KeyError, TypeError, ValueError):
            return

    def get_ai_features(self) -> np.ndarray:
        """Return a row-wise z-score normalized 4xwindow matrix with float32 dtype."""
        if any(len(self.channels[i]) < self.window_size for i in range(self.num_channels)):
            return np.zeros((self.num_channels, self.window_size), dtype=np.float32)

        feature_matrix = np.vstack([list(ch) for ch in self.channels])
        means = np.mean(feature_matrix, axis=1, keepdims=True)
        stds = np.std(feature_matrix, axis=1, keepdims=True) + 1e-8
        normalized_matrix = (feature_matrix - means) / stds
        return normalized_matrix.astype(np.float32)
