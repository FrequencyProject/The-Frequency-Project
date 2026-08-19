#!/usr/bin/env python3
import sys
import serial
import threading
import collections
import numpy as np


class MultiChannelSensorAdapter:

    def __init__(
        self,
        port: str = "/dev/ttyUSB0",
        baudrate: int = 115200,
        window_size: int = 1280,
    ) -> None:
        """Physical hardware adapter bridging edge serial streams to Vivic AI tensors.

<<<<<<< Updated upstream
        Fully compatible across Python 3.10, 3.11, and 3.12 environments.

        :param port: Target file path of device connection (e.g., '/dev/ttyUSB0')
        :param baudrate: Transmission speed matching C++ firmware configs (115200)
        :param window_size: Temporal matrix depth fixed precisely to 1280 samples
        """
        self.port = port
        self.baudrate = baudrate
        self.window_size = window_size
        self.num_channels = 4
=======
class RealHardwareSensorAdapter:
>>>>>>> Stashed changes

        # Deques handle sliding operations natively at O(1) efficiency
        self.channels = [
            collections.deque(maxlen=window_size) for _ in range(self.num_channels)
        ]

        # Asynchronous runtime controls
        self.is_running = False
        self.reader_thread: threading.Thread | None = None
        self.serial_connection: serial.Serial | None = None
        self.data_lock = threading.Lock()

    def connect(self) -> bool:
        """Establishes an active physical connection to the hardware interface."""
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1.0,  # Prevents thread freeze if the device loses power
            )
            # Flush out bootstrap line fragments
            self.serial_connection.reset_input_buffer()
            print(
                f"[HW_BRIDGE] Connected successfully to node connector: {self.port}"
            )
            return True
        except serial.SerialException as e:
            print(
                f"[HW_ERROR] Failed to interface with port {self.port}: {e}",
                file=sys.stderr,
            )
            return False

    def _processing_loop(self) -> None:
        """Background worker thread executing string decoding and numerical extraction loops."""
        # Local pointer binding optimizations for processing efficiency
        num_ch = self.num_channels
        ch_buffers = self.channels
        lock = self.data_lock

        while self.is_running:
            if not self.serial_connection or not self.serial_connection.is_open:
                print(
                    "[HW_ERROR] Active serial node connection lost.",
                    file=sys.stderr,
                )
                self.is_running = False
                break

            try:
                # Ingest incoming byte line terminated by '\n'
                raw_bytes = self.serial_connection.readline()
                if not raw_bytes:
                    continue

                # Decode bytes to text string, safely ignoring drop-out line noise
                line_str = raw_bytes.decode("utf-8", errors="ignore").strip()

                # Dynamic structural parsing gate checking for all 4 expected channels
                if all(f"V{i+1}:" in line_str for i in range(num_ch)):
                    # Expected format: "V1:val,V2:val,V3:val,V4:val"
                    pairs = line_str.split(",")
                    parsed_values = []

                    for pair in pairs:
                        # Maxsplit=1 safeguards against noise inside value fields
                        _, val_str = pair.split(":", 1)
                        parsed_values.append(float(val_str))

                    # Prevent partial matrix state corruption
                    if len(parsed_values) == num_ch:
                        with lock:
                            for i in range(num_ch):
                                ch_buffers[i].append(parsed_values[i])

            except (ValueError, IndexError):
                # Silently catch and discard frames corrupted by hardware clock jitter
                continue
            except Exception as runtime_error:
                print(
                    f"[HW_ERROR] Thread panic triggered by runtime exception: {runtime_error}",
                    file=sys.stderr,
                )
                self.is_running = False

    def start(self) -> None:
        """Spawns the background hardware monitoring thread."""
        if self.serial_connection and self.serial_connection.is_open:
            self.is_running = True
            self.reader_thread = threading.Thread(
                target=self._processing_loop, daemon=True
            )
            self.reader_thread.start()
            print("[HW_BRIDGE] Background telemetry listener running.")
        else:
            print(
                "[HW_ERROR] Start command aborted. No hardware connection active.",
                file=sys.stderr,
            )

    def stop(self) -> None:
        """Clean shutdown handler to protect system socket assignments."""
        self.is_running = False
        if self.reader_thread:
            self.reader_thread.join(timeout=2.0)
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        print("[HW_BRIDGE] Sensor adapter offline.")

    def get_ai_features(self) -> np.ndarray:
        """Compiles historical deques into a normalized matrix tensor block.

        :return: A normalized NumPy matrix of shape (4, 1280) typed as float32
        """
        with self.data_lock:
            # Enforce that the temporal sliding window must be fully saturated before returning data
            if any(
                len(self.channels[i]) < self.window_size
                for i in range(self.num_channels)
            ):
                return np.zeros(
                    (self.num_channels, self.window_size), dtype=np.float32
                )

            # Stack the 4 channels into a single contiguous array block
            feature_matrix = np.vstack([list(ch) for ch in self.channels])

            # Row-independent Z-Score scaling transformation
            # Binds individual channel variance relative strictly to its own historical tracking profile
            means = np.mean(feature_matrix, axis=1, keepdims=True)
            stds = np.std(feature_matrix, axis=1, keepdims=True) + 1e-8
            normalized_matrix = (feature_matrix - means) / stds

            return normalized_matrix.astype(np.float32)
