# 🔒 Local Hardware TPM 2.0 Software Emulation Testing Recipe

This guide details the exact steps required to instantiate a local mock TPM 2.0 server interface to safely validate the `SecureHardwareVault` boundary exception handling mechanisms under isolated simulation criteria.

## 🛠️ Prerequisites & Package Provisioning

Execute this package assembly sequence inside your active **Ubuntu Linux Terminal** window to compile the necessary background software emulation binaries:

```bash
# 1. Update your local kernel package repository indexes
sudo apt-get update

# 2. Install the production-grade IBM TPM 2.0 software emulator layer alongside testing nodes
sudo apt-get install -y swtpm swtpm-tools tpm2-tools
```

## 🎛️ Initializing the Sandbox Virtual Server Bus

To spin up a fully isolated, background mock hardware state engine running on a localized Unix loopback device, execute this orchestration call inside a separate terminal instance:

```bash
# 1. Allocate a secure dedicated runtime state directory partition
mkdir -p /tmp/mytpm

# 2. Launch the swtpm socket process mapping cleanly to character socket controls
swtpm socket --tpmstate dir=/tmp/mytpm --ctrl type=unixio,path=/tmp/mytpm/swtpm-sock --tpm2 --log level=20
```

## 🚀 Validating the Software-Isolated Integrity Tracks

Once the background virtualization socket server is active, configure your active shell path to bypass direct hardware bus checks and connect straight to the mock environment loop:

```bash
# Export the target configuration string to lock onto your localized loopback socket
export TPM2TOOLS_TCTI="unix:path=/tmp/mytpm/swtpm-sock"

# Execute your test suite normally to verify the exception handlers process cleanly
python3 -m pytest
```
