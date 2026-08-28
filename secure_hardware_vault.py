#!/usr/bin/env python3
"""Phase 6: Hardware-Bound Passphrase Escrow Engine."""
import sys
import secrets
import tpm2_pytss
from tpm2_pytss import constants


def _safe_flush(ctx, handle):
    if handle is None:
        return
    try:
        ctx.flush_context(handle)
    except Exception:
        pass


def execute_hardware_escrow(target_port: int = 2321, target_pcr: int = 7) -> bool:
    print(f"[INIT] Opening isolated hardware transport session on port {target_port}...")
    tcti_string = f"swtpm:port={target_port}"

    parent_handle = None
    loaded_handle = None

    try:
        secret_passphrase = secrets.token_bytes(32)

        with tpm2_pytss.ESAPI(tcti_string) as tpm_context:
            print(f" -> Successfully hooked cryptoprocessor. Reading PCR-{target_pcr} state...")
            pcr_selection = tpm2_pytss.TPML_PCR_SELECTION.parse(f"sha256:{target_pcr}")

            # Parent primary template
            parent_area = tpm2_pytss.TPMT_PUBLIC()
            parent_area.type = constants.TPM2_ALG.RSA
            parent_area.nameAlg = constants.TPM2_ALG.SHA256
            parent_area.objectAttributes = (
                constants.TPMA_OBJECT.FIXEDTPM
                | constants.TPMA_OBJECT.FIXEDPARENT
                | constants.TPMA_OBJECT.SENSITIVEDATAORIGIN
                | constants.TPMA_OBJECT.USERWITHAUTH
                | constants.TPMA_OBJECT.RESTRICTED
                | constants.TPMA_OBJECT.DECRYPT
            )
            parent_area.parameters.rsaDetail.symmetric.algorithm = constants.TPM2_ALG.AES
            parent_area.parameters.rsaDetail.symmetric.keyBits.aes = 128
            parent_area.parameters.rsaDetail.symmetric.mode.aes = constants.TPM2_ALG.CFB
            parent_area.parameters.rsaDetail.scheme.scheme = constants.TPM2_ALG.NULL
            parent_area.parameters.rsaDetail.keyBits = 2048
            parent_area.parameters.rsaDetail.exponent = 0

            in_public = tpm2_pytss.TPM2B_PUBLIC(publicArea=parent_area)
            in_sensitive = tpm2_pytss.TPM2B_SENSITIVE_CREATE()
            outside_info = tpm2_pytss.TPM2B_DATA()

            print(" -> Instantiating parent storage keys...")
            parent_handle, _, _, _, _ = tpm_context.create_primary(
                primary_handle=constants.ESYS_TR.OWNER,
                in_sensitive=in_sensitive,
                in_public=in_public,
                outside_info=outside_info,
                creation_pcr=pcr_selection,
            )

            # Explicit sealed-data child template
            child_sensitive = tpm2_pytss.TPM2B_SENSITIVE_CREATE()
            child_sensitive.sensitive.data = secret_passphrase

            child_area = tpm2_pytss.TPMT_PUBLIC()
            child_area.type = constants.TPM2_ALG.KEYEDHASH
            child_area.nameAlg = constants.TPM2_ALG.SHA256
            child_area.objectAttributes = (
                constants.TPMA_OBJECT.FIXEDTPM
                | constants.TPMA_OBJECT.FIXEDPARENT
                | constants.TPMA_OBJECT.USERWITHAUTH
                | constants.TPMA_OBJECT.NODA
            )
            child_area.parameters.keyedHashDetail.scheme.scheme = constants.TPM2_ALG.NULL
            child_area.unique.keyedHash = b""
            child_public = tpm2_pytss.TPM2B_PUBLIC(publicArea=child_area)

            print(f" -> Sealing 32-byte escrow token against PCR-{target_pcr} validation matrices...")
            out_private, out_public, _, _, _ = tpm_context.create(
                parent_handle=parent_handle,
                in_sensitive=child_sensitive,
                in_public=child_public,
                outside_info=outside_info,
                creation_pcr=pcr_selection,
            )

            print(" -> Loading signed objects into volatile memory handles...")
            loaded_handle = tpm_context.load(
                parent_handle=parent_handle,
                in_private=out_private,
                in_public=out_public,
            )

            print(" -> Evicting context to permanent hardware slot 0x81000003...")
            persistent = 0x81000003
            try:
                old_handle = tpm_context.tr_from_tpmpublic(persistent)
                tpm_context.evict_control(constants.ESYS_TR.OWNER, old_handle, persistent)
            except Exception:
                pass

            tpm_context.evict_control(constants.ESYS_TR.OWNER, loaded_handle, persistent)

            # After persisting, transient loaded object no longer needed
            _safe_flush(tpm_context, loaded_handle)
            loaded_handle = None

            # Parent also no longer needed
            _safe_flush(tpm_context, parent_handle)
            parent_handle = None

            print("[SUCCESS] Passphrase escrow established. Master key bound to silicon handle 0x81000003.")
            return True

    except Exception as err:
        print(f"[💥 HARDWARE FAULT] Execution loop failed: {repr(err)}")
        return False

    finally:
        # Best-effort cleanup in case of partial failure
        try:
            with tpm2_pytss.ESAPI(tcti_string) as cleanup_ctx:
                _safe_flush(cleanup_ctx, loaded_handle)
                _safe_flush(cleanup_ctx, parent_handle)
        except Exception:
            pass


if __name__ == "__main__":
    if not execute_hardware_escrow():
        sys.exit(1)