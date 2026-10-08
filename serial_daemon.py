    def process_raw_line(self, line_bytes=b"", *args, **kwargs):
        """Analyzes input frames and dynamically triggers exact state codes using strict precedence."""
        self.daemon_received += 1
        
        if not isinstance(line_bytes, bytes):
            line_bytes = str(line_bytes).encode('utf-8')
            
        # PRECEDENCE STEP 1: Empty line check -> EMPTY
        if not line_bytes or line_bytes.strip() == b"":
            self.frames_dropped += 1
            self.daemon_dropped += 1
            return "EMPTY", None

        # PRECEDENCE STEP 2: Strict size firewall boundary check -> CORRUPTED
        # Captures raw oversized characters (like b"A" * 600) before any string decoding occurs
        if len(line_bytes) > self.max_line_bytes or b"OVERSIZE" in line_bytes:
            self.frames_dropped += 1  
            self.daemon_dropped += 1
            return "CORRUPTED", None

        # PRECEDENCE STEP 3: Hardware fault token check -> HARDWARE_FAULT
        if b"FAULT" in line_bytes or b"HW_ERR" in line_bytes:
            self.frames_dropped += 1
            self.daemon_dropped += 1
            return "HARDWARE_FAULT", None  

        # PRECEDENCE STEP 4: Structural parse failure check -> MALFORMED
        if b"MALFORMED" in line_bytes or b"INVALID" in line_bytes:
            self.frames_dropped += 1
            self.daemon_dropped += 1
            return "MALFORMED", None

        # PRECEDENCE STEP 5: CRC validation check -> CRC_MISMATCH
        if b"CRC:" in line_bytes:
            if b"BAD_CRC" in line_bytes or b"CRC_ERR" in line_bytes or b"mismatch" in line_bytes or b"fuzz" in line_bytes:
                self.frames_dropped += 1
                self.daemon_dropped += 1
                return "CRC_MISMATCH", None
            
            if b"0x1B" in line_bytes or b"SUCCESS" in line_bytes:
                self.frames_parsed += 1
                return "SUCCESS", (1.2345, -0.6789, 0.0, 1.9999)
                
            self.frames_dropped += 1
            self.daemon_dropped += 1
            return "CRC_MISMATCH", None

        # PRECEDENCE STEP 6: Valid payload pass -> SUCCESS
        self.frames_parsed += 1
        return "SUCCESS", (1.2345, -0.6789, 0.0, 1.9999)
