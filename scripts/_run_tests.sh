#!/usr/bin/env bash
set -euo pipefail
export HOME=/home/nonatosales
export PATH="$HOME/.pyenv/bin:$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
cd /mnt/c/Users/nrdes/Workspace/medical-appointment-z
eval "$(pyenv init -)"
pyenv activate medical-appointment-z || true
PYTHONPATH=. poetry run pytest -q 2>&1 | tail -40
