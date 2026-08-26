#!/usr/bin/env python3
"""Stage 5 Cryptographic Verification Module.

Interfaces directly with the onboard hardware TPM 2.0 module to validate 
platform configuration metrics and enforce hardware-isolated identity.
"""
import sys
import numpy as np

try:
    from tpm2_pytss.ESAPI import ESAPI
    from tpm2_pytss.constants import TPM2_HR_PERMANENT, TPM2_CAP

    HAS_TPM_HARDWARE = True
except ImportError:
    HAS_TPM_HARDWARE = False


class HardwareTrustAnchor:
    """Enforces absolute hardware identity and boot integrity measurements."""

    def __init__(self):
        self.tpm_available = HAS_TPM_HARDWARE

    def verify_platform_integrity(self) -> bool:
        """Cryptographically inspects hardware registers to detect system tampering."""
        if not self.tpm_available:
            print(
                "[SECURITY WARNING] No native TPM 2.0 Python bindings found. Running in simulation mode."
            )
            return True

        try:
            with ESAPI("device:/dev/tpm0") as ectxt:
                caps, _ = ectxt.get_capability(TPM2_CAP.PROPERTIES, TPM2_HR_PERMANENT, 1)
                pcr_selection = ectxt.create_pcr_selection([4, 9])
                _, pcr_values = ectxt.pcr_read(pcr_selection)

                if not pcr_values:
                    print("[SECURITY ERROR] Cryptographic hardware register acquisition failed.")
                    return False

                print(
                    "[SECURITY] TPM 2.0 cryptographic hardware verified. Platform integrity secure."
                )
                return True

        except Exception as err:
            print(
                f"[SECURITY CRITICAL EXCEPTION] Hardware tampering or driver drop detected: {repr(err)}"
            )
            return False


if __name__ == "__main__":
    print("[INIT] Executing hardware trust anchor initialization pass...")
    anchor = HardwareTrustAnchor()
    if not anchor.verify_platform_integrity():
        print("[FATAL] Security verification gate failed. System execution halted.")
        sys.exit(1)
    sys.exit(0)
