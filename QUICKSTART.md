# ⏱️ Quick Start (5-Minute Onboarding)

## 1. Environment Setup
Clone the repository and install the verified production package locally:
```bash
git clone https://github.com/FrequencyProject/The-Frequency-Project.git
cd The-Frequency-Project
pip install -e .
```

## 2. Run the Verification Pass
Ensure all 55 master structural, cryptographic, and mathematical invariant tests pass cleanly:
```bash
python3 -m pytest
# Expected output: 55 passed in ~32 seconds
```

## 3. Launch the Operational Engine
Execute a localized simulation cycle to see the telemetry data pipelines and latent monitors initialize:
```bash
python3 run_session.py
```

## 4. Run via Production Container
Compile and boot the hardened, unprivileged zero-trust edge image:
```bash
sudo docker build -t the-frequency-project:edge .
sudo docker run --rm -it the-frequency-project:edge
```

**What is next?** → Read `README.md` for full deployment, hardware pins, and configuration variables.
