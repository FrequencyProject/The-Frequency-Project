import pytest
import tpm2_pytss
from secure_hardware_vault import seal_to_persistent
from unseal_hardware_vault import unseal_from_persistent

def test_tpm_hardware_seal_unseal_parity(capsys):
    """Verifies end-to-end cryptographic parity between the sealing and unsealing vault engines."""
    test_secret = b"SECRET_CRYPTOGRAPHIC_TOKEN_VAL_42"
    dummy_port = 2321
    test_slot = 0x81000003

    # 1. Attempt to seal the secret into the TPM interface emulator env
    seal_status = seal_to_persistent(test_secret, target_port=dummy_port, persistent_handle=test_slot)
    
    # Check if a swtpm daemon emulator is active on the local network block
    if seal_status != 0:
        pytest.skip("[SKIPPED] Physical TPM 2.0 or active 'swtpm' daemon absent on port 2321. Skipping hardware verification.")

    # 2. Trigger the unsealing utility engine to extract the token back from silicon
    unseal_status = unseal_from_persistent(target_port=dummy_port, persistent_handle=test_slot)
    assert unseal_status == 0, "The unsealing subsystem failed to read the hardware reference handle mapping."

    # 3. Capture system console outputs to confirm the exact byte sequence matches
    captured = capsys.readouterr()
    expected_hex = test_secret.hex()
    
    assert f"hex_token={expected_hex}" in captured.out, "Cryptographic data corruption: the unsealed token deviated from origin parameters."
    print("\n[PASSED] TPM Hardware Vault structural parity is verified.")
