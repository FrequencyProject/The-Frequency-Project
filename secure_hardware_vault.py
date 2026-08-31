#!/usr/bin/env python3
"""Phase 6: Hardware-Bound Passphrase Provisioning Utility.

Leverages a memory-managed ESAPI session to seal high-entropy storage 
master keys under a PCR policy and provisions them into persistent slot 0x81000003.
"""
import os
import sys
import logging
import tpm2_pytss
from tpm2_pytss import constants, TPM2B_SENSITIVE_DATA, TPM2B_PUBLIC

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')
logger = logging.getLogger("HardwareVault")

def seal_to_persistent(secret_data: bytes, target_port: int = 2321, persistent_handle: int = 0x81000003, pcr_index: int = 7) -> int:
    """Seals a high-entropy secret under a PCR configuration policy and persists it into the TPM."""
    if not secret_data:
        logger.error("No secret data provided for sealing operation.")
        return 1

    # 1. REMEDIATION: Strict boundary check to prevent out-of-bounds PCR registry errors
    if not (0 <= pcr_index < 24):
        logger.error(f"Invalid PCR index configuration: {pcr_index}. Range must stay within [0-23].")
        return 1

    logger.info(f"Opening isolated hardware provisioning session on port {target_port}...")
    tcti_string = f"swtpm:port={target_port}"
    
    policy_session = None
    transient_handle = None
    tpm_context = None

    try:
        tpm_context = tpm2_pytss.ESAPI(tcti_string)
        
        logger.info("Reading primary storage hierarchy handles...")
        primary_handle = tpm_context.get_primary_handle(constants.TPM2_RH_OWNER)
        
        logger.info(f"Calculating authorization policy metrics for PCR-{pcr_index}...")
        policy_session = tpm_context.start_auth_session(
            tpm2_pytss.TPM_SE.POLICY,
            constants.TPM2_ALG_SHA256
        )
        
        pcr_selection = tpm2_pytss.TPML_PCR_SELECTION.parse(f"sha256:{pcr_index}")
        tpm_context.policy_pcr(policy_session, pcr_selection)
        policy_digest = tpm_context.policy_get_digest(policy_session)

        logger.info("Configuring public structures with strict hardware authorization rules...")
        public_template = TPM2B_PUBLIC()
        public_template.publicArea.type = constants.TPM2_ALG_KEYEDHASH
        public_template.publicArea.nameAlg = constants.TPM2_ALG_SHA256
        
        # 2. REMEDIATION: Fixed conflicting authorization flags to prevent physical TPM rejection
        public_template.publicArea.objectAttributes = (
            constants.TPMA_OBJECT_FIXEDTPM |
            constants.TPMA_OBJECT_FIXEDPARENT |
            constants.TPMA_OBJECT_ADMINWITHPOLICY
        )
        public_template.publicArea.authPolicy = policy_digest
        public_template.publicArea.parameters.keyedHashDetail.scheme.scheme = constants.TPM2_ALG_NULL

        sensitive_input = TPM2B_SENSITIVE_DATA(secret_data)

        logger.info("Generating ephemeral object within primary hierarchy node...")
        private_blob, public_blob, _, _, _ = tpm_context.create(
            primary_handle,
            in_sensitive=sensitive_input,
            in_public=public_template
        )

        transient_handle = tpm_context.load(primary_handle, private_blob, public_blob)

        logger.info(f"Checking for persistent handle slot collisions on index 0x{persistent_handle:08X}...")
        try:
            stale_ref = tpm_context.tr_from_tpmpublic(persistent_handle)
            tpm_context.evict_control(constants.TPM2_RH_OWNER, stale_ref, persistent_handle)
            logger.info("Successfully evicted existing stale persistent handle slot collision.")
        except tpm2_pytss.TSS2_Exception as tss_err:
            # 3. REMEDIATION: Narrow exception handling block to safely filter unallocated slots vs errors
            if "handle does not exist" in str(tss_err) or tss_err.rc == 0x018F:
                logger.info("Persistent handle target slot is currently unallocated and free.")
            else:
                logger.warning(f"Eviction sequence passed with non-critical warning exception: {repr(tss_err)}")
        except Exception as generic_err:
            logger.warning(f"Generic internal eviction exception logged: {repr(generic_err)}")

        tpm_context.evict_control(constants.TPM2_RH_OWNER, transient_handle, persistent_handle)
        logger.info(f"Provisioning complete. Secret permanently written to TPM NV slot 0x{persistent_handle:08X}.")
        return 0

    except Exception as err:
        logger.error(f"Cryptographic provisioning session aborted due to hardware fault: {repr(err)}")
        return 1
        
    finally:
        if tpm_context is not None:
            try:
                if policy_session is not None:
                    tpm_context.flush_context(policy_session)
                if transient_handle is not None:
                    tpm_context.flush_context(transient_handle)
            except Exception:
                pass
            finally:
                try:
                    tpm_context.close()
                except Exception:
                    pass

if __name__ == "__main__":
    TARGET_PORT = int(os.getenv("TPM_PORT", "2321"))
    TARGET_SLOT = int(os.getenv("TPM_SLOT", "0x81000003"), 16)
    TARGET_PCR = int(os.getenv("TPM_PCR_INDEX", "7"))

    sample_production_token = b"PROD_ENC_KEY_VIVIC_MATRIX_9944A"
    sys.exit(seal_to_persistent(sample_production_token, target_port=TARGET_PORT, persistent_handle=TARGET_SLOT, pcr_index=TARGET_PCR))
