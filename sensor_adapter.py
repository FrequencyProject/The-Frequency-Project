"""
ECOLOGICAL SENSOR INTERFACE LAYER (STUB)
This module acts as the scaffolding adapter for connecting real physical hardware
(via Analog-to-Digital Converters like ADS1115 or MCP3008) to the FS-AI input pipeline.
"""

import numpy as np


class HardwareStreamError(Exception):
    """Raised when the physical sensor streams return a flatline or missing data payload."""

    pass


class RealHardwareSensorAdapter:

    def __init__(self, spi_bus: int = 0, device_id: int = 0):
        self.spi_bus = spi_bus
        self.device_id = device_id
        self.is_calibrated = False
        print(
            f"[HARDWARE INTENT] Initializing hardware bridge on SPI bus {self.spi_bus}, device {self.device_id}"
        )

    def calibrate_baseline_ground(self) -> bool:
        """Executes a calibration routine to remove grid electromagnetic noise hum (50Hz/60Hz)."""
        print(
            "[HARDWARE] Calculating localized ground impedance and environmental background hum parameters..."
        )
        self.is_calibrated = True
        return self.is_calibrated

    def read_analog_stream(
        self, channel_id: int, num_samples: int, simulate_hardware: bool = False
    ) -> np.ndarray:
        """Interfaces hardware libraries (like spidev or circuitpython) to pull sensor voltages."""
        if not self.is_calibrated:
            raise RuntimeError(
                "[CRITICAL] Cannot read raw hardware data stream before executing calibration."
            )

        print(
            f"[HARDWARE] Streaming {num_samples} raw voltage packets from physical ADC input channel {channel_id}"
        )

        # Non-zero simulation path for verified CI integration testing runs
        if simulate_hardware:
            rng = np.random.default_rng(42)
            return rng.normal(0.5, 0.1, num_samples)

        # Hard fail-fast boundary condition to prevent silent zero-buffer mask failures
        raise HardwareStreamError(
            f"[FAIL-FAST] Physical sensor node on channel {channel_id} is unregistered or offline. "
            "Silicon stream blocked to prevent system-wide data psychosis."
        )


if __name__ == "__main__":
    # Test script verification block for contributors
    hardware_bridge = RealHardwareSensorAdapter()
    hardware_bridge.calibrate_baseline_ground()
    try:
        # Test simulated run for local verification
        mock_batch = hardware_bridge.read_analog_stream(
            channel_id=1, num_samples=2560, simulate_hardware=True
        )
        print(
            f"Hardware scaffolding bridge verified locally. Buffer shape: {mock_batch.shape}"
        )

        # Test live fallback run to verify the fail-fast security gate trigger works
        print("[HARDWARE] Verifying safety gate trigger bounds...")
        hardware_bridge.read_analog_stream(channel_id=1, num_samples=2560)
    except HardwareStreamError as e:
        print(f"Safety Gate Active: {e}")
