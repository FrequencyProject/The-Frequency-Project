import numpy as np
import threading
import logging
from serial_daemon import HardwareSerialDaemon

logger = logging.getLogger("SensorAdapter")


class TelemetryCircularBuffer:
    def __init__(self, window_size: int = 1280):
        self.window_size = window_size
        self.lock = threading.RLock()
        self._buf_capacity = window_size * 2
        self._circular_buffer = np.zeros((4, self._buf_capacity), dtype=np.float32)
        self._head = 0
        self._count = 0

    def push(self, data_tuple: tuple):
        with self.lock:
            idx = self._head
            self._circular_buffer[0, idx] = float(data_tuple[0])
            self._circular_buffer[1, idx] = float(data_tuple[1])
            self._circular_buffer[2, idx] = float(data_tuple[2])
            self._circular_buffer[3, idx] = float(data_tuple[3])

            self._circular_buffer[0, idx + self.window_size] = float(data_tuple[0])
            self._circular_buffer[1, idx + self.window_size] = float(data_tuple[1])
            self._circular_buffer[2, idx + self.window_size] = float(data_tuple[2])
            self._circular_buffer[3, idx + self.window_size] = float(data_tuple[3])

            self._head = (self._head + 1) % self.window_size
            if self._count < self.window_size:
                self._count += 1

    def get_window_view(self, destination_matrix: np.ndarray) -> bool:
        with self.lock:
            if self._count < self.window_size:
                return False
            start_idx = self._head
            destination_matrix[:, :] = self._circular_buffer[:, start_idx : start_idx + self.window_size]
            return True


class FeatureCompiler:
    def __init__(self, window_size: int = 1280):
        self.window_size = window_size

    def process_window(self, source_matrix: np.ndarray) -> np.ndarray:
        output_matrix = np.zeros_like(source_matrix)
        for i in range(4):
            ch_data = source_matrix[i, :]
            mean = np.mean(ch_data)
            std = np.std(ch_data)
            if std > 1e-8:
                output_matrix[i, :] = (ch_data - mean) / std
            else:
                output_matrix[i, :] = ch_data - mean
        return output_matrix


class SensorAdapter:
    def __init__(self, port: str = "COM3", baudrate: int = 115200, window_size: int = 1280, *args, **kwargs):
        self.window_size = window_size
        self._buffer_manager = TelemetryCircularBuffer(window_size=window_size)

        # Dual-attribute layout mapping to guarantee backward compatibility with all test modules
        self._compiler = FeatureCompiler(window_size=window_size)
        self._feature_compiler = self._compiler

        self.lock = self._buffer_manager.lock
        self._shared_feature_matrix = np.zeros((4, window_size), dtype=np.float32)

        self.daemon = HardwareSerialDaemon(
            port=port,
            baudrate=baudrate,
            callback=self._packet_ingestion_callback,
            *args, **kwargs
        )
        self.frames_received = 0
        self.frames_dropped = 0

    @property
    def _circular_buffer(self):
        return self._buffer_manager._circular_buffer

    @property
    def _count(self):
        return self._buffer_manager._count

    @_count.setter
    def _count(self, value):
        self._buffer_manager._count = value

    @property
    def _head(self):
        return self._buffer_manager._head

    @_head.setter
    def _head(self, value):
        self._buffer_manager._head = value

    def _packet_ingestion_callback(self, data_tuple: tuple):
        """Reject unsafe live telemetry and buffer validated four-channel frames."""
        if not data_tuple or len(data_tuple) != 4:
            self.frames_dropped += 1
            return

        is_simulation_active = getattr(self.daemon, "simulation_active", False)

        if not is_simulation_active:
            try:
                if any(abs(float(voltage)) >= 2.0480 for voltage in data_tuple):
                    self.frames_dropped += 1
                    logger.critical(
                        "[HARDWARE ALERT] Clipping saturation boundary overrun; dropping live frame: %r",
                        data_tuple,
                    )
                    return
            except (TypeError, ValueError) as exc:
                self.frames_dropped += 1
                logger.critical(
                    "[HARDWARE ALERT] Non-numeric live telemetry frame; dropping frame: %r; error=%s",
                    data_tuple, exc,
                )
                return

        with self.lock:
            self.frames_received += 1
            self._buffer_manager.push(data_tuple)

    def process_incoming_packet(self, raw_input: str | bytes | None, allow_missing_crc: bool = False):
        if raw_input is None:
            return
        try:
            raw_bytes = raw_input if isinstance(raw_input, bytes) else str(raw_input).encode('utf-8')
            stripped = raw_bytes.strip()
            if not stripped:
                return

            if b',CRC:0x' not in stripped:
                if not allow_missing_crc:
                    self.frames_dropped += 1
                    return
                calculated_crc = self.daemon.compute_binary_crc8(stripped)
                raw_bytes = stripped + b',CRC:0x' + f'{calculated_crc:02X}'.encode('utf-8') + b'\n'

            status, parsed_tuple = self.daemon.process_raw_line(raw_bytes)
            if status == 'SUCCESS' and parsed_tuple:
                self._packet_ingestion_callback(parsed_tuple)
            else:
                self.frames_dropped += 1
        except Exception:
            self.frames_dropped += 1

    def start_acquisition(self):
        self.daemon.start()

    def stop_acquisition(self):
        self.daemon.stop()

    def get_raw_features(self) -> np.ndarray:
        matrix = np.zeros((4, self.window_size), dtype=np.float32)
        with self.lock:
            self._buffer_manager.get_window_view(matrix)
        return matrix

    def get_ai_features(self) -> np.ndarray:
        raw_matrix = self.get_raw_features()
        with self.lock:
            return self._compiler.process_window(raw_matrix)


MultiChannelSensorAdapter = SensorAdapter
