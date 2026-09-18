#!/bin/sh
set -eu

echo "[ENTRYPOINT] Launching pre-flight infrastructure validation checks..."
python validate_config.py

echo "[ENTRYPOINT] Handing execution PID 1 over to the core runtime session..."
exec python run_session.py
