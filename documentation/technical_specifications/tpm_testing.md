# 🔒 Hardware Security Vault: Local TPM 2.0 Emulation Recipe

This document details the exact configuration profiles required to instantiate a localized software emulator socket layer. This allows high-assurance verification of the cryptographic exception taxonomy without needing physical access to an active motherboard TPM 2.0 chip.

## 🛠️ Prerequisites & Package Provisioning

To simulate a secure communication bus natively inside your Linux subsystem (WSL2), run the following installation pass inside the Ubuntu terminal to pull down the core emulation binaries:

```bash
# Update local package indexes and install the standard IBM swtpm emulator suite
sudo apt-get update
sudo apt-get install -y swtpm swtpm-tools tpm2-tools
```

## 🌌 Instantiating the Isolated Software Socket

To provision a detached emulator workspace directory and launch the background socket proxy without triggering low-level hardware bus discovery loops, execute this terminal sequence:

```bash
# 1. Create a dedicated state storage directory partition
mkdir -p /tmp/mytpm

# 2. Spin up the swtpm daemon bound cleanly to local port 2321
swtpm socket --tpmstate dir=/tmp/mytpm \
             --tpm2 \
             --server port=2321 \
             --ctrl port=2322 \
             --flags startup-clear &
```

## 🛡️ Linking the Environment Transport Interface

To instruct the `tpm2-pytss` library to bypass direct physical motherboard scans and route all cryptographic payloads straight into your new local software socket, export the following TCTI (TPM Command Transmission Interface) parameters into your active terminal shell or testing profiles:

```bash
# Direct transport flags guiding the execution engine to the mock socket proxy
export TPM2TOOLS_TCTI="mssim:port=2321"
export TPM_TCTI_INTERFACE="mssim:port=2321"
```

## 📋 Expected Verification Policy States

When your unit tests execute on top of this emulation socket, the cryptographic vault boundary verifies three distinct state invariants:

1. **Fallback/Software State (`tcti_profile="none"`):** Bypasses hardware scans completely. The initialization layer returns `True` and locks the tracking parameter to `is_sealed = False`.
2. **Transient Line Jitter (`rc = 0x101`):** Simulates low-level SPI bus timeouts. The system catches the `IOError`, logs a warning warning, and triggers an automatic 3-pass retry loop.
3. **Policy Tampering Breach (`rc = 0x9A`):** Indicates a PCR-7 verification mismatch. The interface instantly interrupts operations and raises a high-severity `TPMSecurityBreachError` to lock down the system perimeter.
