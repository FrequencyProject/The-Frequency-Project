#!/usr/bin/env python3
"""Phase 6: Hardware-Bound Passphrase Retrieval Utility.

Leverages a single, memory-managed ESAPI session to unseal the 
high-entropy storage master keys from persistent slot 0x81000003.
"""
import sys
import tpm2_pytss
from tpm2_pytss import constants

def unseal_from_persistent(target_port: int = 2321, persistent_handle: int = 0x81000003) -> int:
    print(f"[INIT] Opening isolated hardware retrieval session on port {target_port}...")
    tcti_string = f"swtpm:port={target_port}"

    try:
        # Open a single, memory-managed connection to extract the passphrase
        with tpm2_pytss.ESAPI(tcti_string) as tpm_context:
            print(f" -> Resolving persistent hardware index 0x{persistent_handle:08X}...")
            
            # Map the persistent index into the active session tracking table
            obj_handle = tpm_context.tr_from_tpmpublic(persistent_handle)

            print(" -> Verifying PCR-7 policy state and executing unseal operation...")
            unsealed_data = tpm_context.unseal(obj_handle)

            # Extract the raw byte contents safely from the returned TSS2 data block structure
            data = bytes(unsealed_data.buffer) if hasattr(unsealed_data, "buffer") else bytes(unsealed_data)

            print(f"[SUCCESS] Unseal operation verified. Extracted {len(data)} bytes from silicon.")
            print(f"hex_token={data.hex()}")
            return 0

    except Exception as err:
        print(f"[💥 HARDWARE FAULT] Unseal extraction failed: {repr(err)}")
        print("[HINT] If this error tracks a policy block, the active boot state values of PCR-7 shifted.")
        return 1

if __name__ == "__main__":
    sys.exit(unseal_from_persistent())
