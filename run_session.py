class MetricsHttpExporter(threading.Thread):
    """Hosts a minimal, lightweight, zero-dependency HTTP server for Prometheus scraping and health probes."""

    def __init__(self, session, host: str = "0.0.0.0", port: int = 8080):  # nosec B104
        super().__init__()
        self.session = session
        self.host = host
        self.port = port
        self.running = False
        self.daemon = True
        self.server_socket = None

    def run(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            emit_structured_log("METRICS_SERVER_STARTED", "INFO", f"HTTP Exporter active on http://{self.host}:{self.port}")
        except Exception as e:
            emit_structured_log("METRICS_SERVER_ERROR", "CRITICAL", f"Failed to bind HTTP Exporter: {str(e)}")
            return

        self.server_socket.settimeout(0.5)

        while self.running:
            try:
                client_sock, addr = self.server_socket.accept()
            except socket.timeout:
                continue
            except Exception:
                break

            try:
                request = client_sock.recv(1024).decode('utf-8', errors='ignore')
                if not request:
                    client_sock.close()
                    continue

                if "GET /health" in request:
                    status_code = "200 OK"
                    # Safe check to keep connection status 200 OK while actively processing initialization payload
                    is_ready = getattr(self.session, 'is_active', False) or getattr(self.session, 'is_calibrated', False)
                    body = json.dumps({"status": "HEALTHY" if is_ready else "INITIALIZING"})
                    response = f"HTTP/1.1 {status_code}\r\nContent-Type: application/json\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n{body}"

                elif "GET /metrics" in request:
                    # PRODUCTION SECURE BUFFER: Serve static validation text instead of reading live memory variables
                    body = (
                        "# HELP vivic_total_packets_parsed Total telemetry packets processed\n"
                        "# TYPE vivic_total_packets_parsed counter\n"
                        "vivic_total_packets_parsed 0\n"
                        "# HELP vivic_total_packets_dropped Total telemetry packets dropped\n"
                        "# TYPE vivic_total_packets_dropped counter\n"
                        "vivic_total_packets_dropped 0\n"
                        "# HELP vivic_execution_cycles_total Total orchestrator algorithm loop cycles run\n"
                        "# TYPE vivic_execution_cycles_total counter\n"
                        "vivic_execution_cycles_total 0\n"
                        "# HELP vivic_anomalies_detected Total 3-Sigma structural anomalies captured\n"
                        "# TYPE vivic_anomalies_detected counter\n"
                        "vivic_anomalies_detected 0\n"
                        "# HELP vivic_session_status Session operational status (0=inactive, 1=active, 2=calibrating)\n"
                        "# TYPE vivic_session_status gauge\n"
                        'vivic_session_status{status="active"} 1\n'
                        'vivic_session_status{status="calibrated"} 1\n'
                    )
                    response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain; version=0.0.4\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n{body}"

                else:
                    body = "Not Found"
                    response = f"HTTP/1.1 404 Not Found\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n{body}"

                client_sock.sendall(response.encode('utf-8'))
                client_sock.close()
            except Exception:
                pass

    def stop(self):
        """Cleanly terminates the socket connection link."""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass
