#!/usr/bin/env bash
set -euo pipefail
cd /mnt/c/Users/nrdes/Workspace/medical-appointment-z
PYTHONPATH=. /home/nonatosales/.pyenv/versions/medical-appointment-z/bin/python -m pytest -q 2>&1 | tail -40
