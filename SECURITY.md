# 🛡️ Security & Architectural Maturity Policy
> **Document Status: Technical Audit v1.3 (Factual Production Baseline)**

This policy defines the cryptographic boundary, runtime safety parameters, and hardware isolation constraints of the Vivic AI architecture. It explicitly delineates between active mathematical code controls and planned hardware deployment perimeters.

---

### 🔒 1. Active Implementation Metrics (Current Status)

The current repository codebase operates as a production-grade functional data-ingestion system. The following security controls are active within the current version framework:

#### 🔹 1.1 Input Ingestion Sanitization
The stream processing layer implements deterministic syntax validation gates (`ValueError` and `IndexError` exception handling blocks). This ensures that malformed serial strings, partial transmissions, or frame drops caused by line noise are caught and discarded at the boundary, preventing unparsed data from destabilizing downstream memory structures.

#### 🔹 1.2 Algorithmic Stability and Numerical Controls
The Z-score scaling matrix transformation incorporates a hardcoded static numerical modifier ($\epsilon = 1e^{-8}$). During physical sensor flatlines or zero-variance conditions, this bounding variable prevents computational lockups, mathematical instability, or division-by-zero runtime exceptions, keeping the output matrix structurally sound.

#### 🔹 1.3 Execution Determinism and State Replication
To ensure exact experimental replication across distinct evaluation runtimes, all synthetic signal generation routines avoid global state seeding. Instead, the testing environment utilizes thread-safe, isolated pseudo-random number generator instances (`np.random.default_rng`), preventing thread race conditions or shared memory corruption.

#### 🔹 1.4 Cryptographic Hardware Abstraction & Granular Fault Isolation
The repository features an integrated Trusted Platform Module interface (`secure_hardware_vault.py`). It explicitly decouples hardware transmission line jitter from structural policy breaches:
- **Transient Line Jitter (0x101):** Triggers an automatic, non-blocking 3-pass retry loop to allow line voltages to settle.
- **Policy Tampering Breach (0x9A):** Triggers an immediate system perimeter lock state by raising a high-severity `TPMSecurityBreachError`.
- **Local Simulation:** Supports hardware-isolated key unsealing emulation via a local `swtpm` software socket proxy.

#### 🔹 1.5 Hardened Containerization & Volatile Sandboxing
The deployment matrix leverages a multi-stage BuildKit image configuration (`Dockerfile`) to enforce zero-trust runtime parameters:
- **Rootless Execution:** Processes execute strictly under a non-privileged user profile (`UID 10001`) to prevent container-breakout escalation hazards.
- **Immutable Source Invariant:** The entire application workspace root is locked under a read-only filesystem profile (`chmod 0555`). 
- **Volatile Partitions:** Ephemeral state operations and logs are restricted to a volatile, memory-backed `64MB` RAM disk (`tmpfs` mounted at `/tmp`).

#### 🔹 1.6 Automated Security & Supply Chain Guardrails
The GitHub Actions CI pipeline (`.github/workflows/ci.yml`) executes real-time security scans on every branch commit before deployment:
- **Bandit Linter:** Scans for code-level security vulnerabilities (e.g., wildcard socket binds), enforced with inline tracking exclusions (`# nosec`).
- **pip-audit Scanner:** Scans for active CVE vulnerabilities within downstream Python dependencies.
- **Dependency Version Pinning:** Enforces strict upper/lower bounds on third-party libraries (e.g., `cryptography<=42.0.8`) inside `pyproject.toml`.

---

### 🗺️ 2. Advanced Security Perimeters (Target Roadmap Lifecycle)

The specialized security perimeters outlined below represent the project's formalized architectural production targets. These mechanisms are currently in the design and planning phases and require integration with physical target hardware.

#### 🚀 Phase 1: Runtime Sandbox Isolation (Development Backlog)
*   **Target Objective:** Insulate the host computing operating system from potential zero-day supply chain vulnerability exploits within processing dependencies.  
*   **Planned Mechanism:** The ingestion and parsing pipelines will be wrapped within isolated, ephemeral micro-virtual machine containers (**microVMs**, such as AWS Firecracker). The sandbox runtime will execute within a strictly partitioned, read-only root file-system with zero persistent storage write privileges, automatically destroying and recreating its environment snapshot on a rolling 60-second timer to clear volatile memory spaces.

#### 🔒 Phase 2: Hardware Asymptotic Saturation Guards (Engineering Roadmap)
*   **Target Objective:** Protect downstream analog-to-digital converter (ADC) registers and neural network inference layers from electrical damage during extreme atmospheric anomalies (e.g., lightning strikes or severe electrostatic discharge).  
*   **Planned Mechanism:** The Analog Front End (AFE) circuit topology will implement a hardware-level **Transient Voltage Suppression (TVS) Diode Matrix** combined with a fast-acting electronic fuse (e-Fuse). If voltage rate-of-change surges ($\Delta_{v}$) exceed structural threshold constraints within a $< 2\text{ms}$ window, a physical crowbar isolation loop clamps the line to ground, replaces the input channel data with a maximum-entropy placeholder, and logs a "Telemetry Blindspot" warning state flag.

---

### 🔍 3. Threat Model Matrix

| Threat Class | Vector Channel | Implemented Software Mitigations | Target Hardware Roadmap |
| :--- | :--- | :--- | :--- |
| **Malformed Data Injection** | Corrupted Serial Frame Text | Boundary parsing exception blocks reject dirty strings. | None (Fully resolved in software). |
| **Telemetry Spoofing** | Injection of synthetic/false frequencies | `secure_hardware_vault.py` TPM 2.0 session initialization check layers. | Native edge microcontroller hardware-isolated signing. |
| **Physical Overvoltage** | Electrostatic discharge or lightning strikes | Digital software clamp limits float ranges. | TVS Diode arrays + Hardware Crowbar isolation circuit. |
| **Dependency Hijack** | Vulnerabilities in parsing libraries | Strict version pinning + Bandit scans + `pip-audit` pipeline. | Read-only ephemeral microVM runtime isolation. |
