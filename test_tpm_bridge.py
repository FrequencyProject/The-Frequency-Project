#!/usr/bin/env python3
"""Cross-Environment Virtual Cryptoprocessor Handshake Validator.

Bridges the Windows application space straight into the WSL2 Linux TPM 2.0 
simulator socket to verify remote transport visibility and handshake parity.
"""
import sys
import tpm2_pytss
from tpm2_pytss import constants


def verify_virtual_tpm_bridge(target_port: int = 2321) -> bool:
    """Attempts a clean cryptographic transport handshake with the listening Ubuntu daemon."""
    print(
        f"[INIT] Opening network transport bridge to virtual silicon socket on port {target_port}..."
    )

    # Establish the transport layer connection string using the swtpm loop driver format
    tcti_string = f"swtpm:port={target_port}"

    try:
        # Initialize the native TCG software stack context engine across the OS boundary
        with tpm2_pytss.ESAPI(tcti_string) as tpm_context:
            print(
                "[BRIDGE SUCCESS] Network handshake established with the virtual cryptoprocessor."
            )

            # Query the standard capability blocks using the correct constants sub-module paths
            caps, _ = tpm_context.get_capability(
                constants.TPM2_CAP.TPM_PROPERTIES, constants.TPM2_PT.NONE, 1
            )

            print(f" -> Simulated Silicon Capability Logs: {repr(caps)}")
            print(
                "[SUCCESS] Cross-environment cryptographic transport pipeline is fully operational."
            )
            return True

    except Exception as err:
        print(f"[💥 BRIDGE FAILURE] Connection refused or transport driver failed: {repr(err)}")
        print(
            " -> Verify that 'swtpm' is actively running inside your Ubuntu terminal window on port 2321."
        )
        return False


if __name__ == "__main__":
    success = verify_virtual_tpm_bridge()
    if not success:
        sys.exit(1)
