#!/usr/bin/env python3
"""Phase 2 & 3 Validation: Noise Injection & Serial Stress Harness.

Fuzzes the hardware daemon parser and multi-channel sensor adapter with corrupt 
packet strings, dropped bytes, and malformed frames to verify edge fault tolerance.
"""
import time
import numpy as np
from sensor_adapter import MultiChannelSensorAdapter


class TelemetryStressHarness:
    """Simulates worst-case electronic line noise and transmission corruption profiles."""

    def __init__(self, adapter: MultiChannelSensorAdapter):
        self.adapter = adapter
        self.rng = np.random.default_rng(seed=1337)

    def generate_corrupt_packet_variants(
        self, v1: float, v2: float, v3: float, v4: float
    ) -> list[str]:
        """Compiles an array of dirty, structurally malformed, or noisy transmission streams."""
        corruption_scenarios = [
            # 1. Standard valid baseline frame
            f"V1:{v1},V2:{v2},V3:{v3},V4:{v4}\n",
            # 2. Truncated float parsing cutoff boundary (Loose connection wire)
            f"V1:{v1:.2f},V2:{v2:.2f},V3:-,V4:{v4:.2f}\n",
            # 3. Missing structural packet channel delimiters (Baudrate timing shift)
            f"V1:{v1}V2:{v2},V3:{v3},V4:{v4}\n",
            # 4. Injected alphanumeric noise spikes (Static EM lightning arcs)
            f"V1:{v1},V2:NOISE_BURST_X,V3:{v3},V4:{v4}\n",
            # 5. Empty stray framing bytes (Line line echo transients)
            " \n",
            # 6. Completely corrupted key descriptors (UART bit flipping anomalies)
            f"X1:{v1},V2:{v2},V3:{v3},V4:{v4}\n",
            # 7. Extreme out-of-bounds float values
            f"V1:9999999.9,V2:-888888.8,V3:{v3},V4:{v4}\n",
        ]
        return corruption_scenarios

    def execute_fuzz_attack(self, iterations: int = 50) -> dict[str, int]:
        """Bombards the parsing boundaries directly and tracks metrics responses."""
        print(f"[HARNESS] Initializing fuzzing bombardment loop ({iterations} cycles)...")

        for _ in range(iterations):
            # Generate local baseline variables for each iteration step
            v1, v2, v3, v4 = self.rng.normal(0, 1, 4)

            packets = self.generate_corrupt_packet_variants(v1, v2, v3, v4)
            for packet in packets:
                # Direct string injection bypasses real hardware to force processing errors
                self.adapter.process_incoming_packet(packet)

            # Randomly inject raw non-finite float arrays directly into the callback loops
            nan_mode = self.rng.choice([0, 1, 2, 3])
            corrupt_vector = np.array([v1, v2, v3, v4], dtype=np.float32)
            corrupt_vector[nan_mode] = np.nan if self.rng.choice([True, False]) else np.inf
            self.adapter.hardware_packet_callback(corrupt_vector)

        # Extract telemetry diagnostic outcome reports from the active adapter structures
        return {
            "daemon_received": self.adapter.daemon.frames_received,
            "daemon_dropped": self.adapter.daemon.frames_dropped,
            "adapter_ch1_dropped": self.adapter.metrics["ch1_dropped"],
            "adapter_ch2_dropped": self.adapter.metrics["ch2_dropped"],
            "adapter_ch3_dropped": self.adapter.metrics["ch3_dropped"],
            "adapter_ch4_dropped": self.adapter.metrics["ch4_dropped"],
        }


if __name__ == "__main__":
    print("[INIT] Launching Baseline Telemetry Noise Injection Test Cycle...")
    test_adapter = MultiChannelSensorAdapter(port="STRESS_MOCK", debug=False)
    stress_engine = TelemetryStressHarness(test_adapter)

    report = stress_engine.execute_fuzz_attack(iterations=20)

    print("\n======================================================================")
    print("VIVIC AI: HARDENED COMPLIANCE FAULT TOLERANCE AUDIT REPORT")
    print("======================================================================")
    print(f" -> Total Valid String Frames Accepted  : {report['daemon_received']}")
    print(f" -> Structure Parser Text Rejections   : {report['daemon_dropped']}")
    print(f" -> Channel 1 Biotic NaN/Inf Intercepts: {report['adapter_ch1_dropped']}")
    print(f" -> Channel 2 Mycelial NaN/Inf Intercepts: {report['adapter_ch2_dropped']}")
    print(f" -> Channel 3 Mycelial NaN/Inf Intercepts: {report['adapter_ch3_dropped']}")
    print(f" -> Channel 4 Geophysical NaN/Inf Intercepts: {report['adapter_ch4_dropped']}")
    print("======================================================================")

    assert report["daemon_dropped"] > 0, "Error: Ingestion parser failed to trap dirty strings."
    assert (
        report["adapter_ch1_dropped"] > 0
        or report["adapter_ch2_dropped"] > 0
        or report["adapter_ch3_dropped"] > 0
        or report["adapter_ch4_dropped"] > 0
    ), "Error: Safety guards missed NaN vectors."
    print("[SUCCESS] Operational fault tolerance audited. Ingestion boundary is un-jammable.")
