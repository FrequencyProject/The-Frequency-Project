#!/bin/sh
# Exit immediately if any command returns a non-zero exit status code
set -e

echo "[INIT] Launching pre-flight container validation checks..."
python validate_config.py

echo "[EXEC] Substituting container shell process with main orchestrator thread..."
# The native exec command replaces the parent shell process slot entirely.
# This assigns PID 1 straight to Python so it intercepts OS signals (SIGTERM) gracefully.
exec python run_session.py
