#!/usr/bin/env bash
set -euo pipefail
cd /mnt/c/Users/nrdes/Workspace/medical-appointment-z
source ~/.pyenv/versions/3.12.13/envs/medical-appointment-z/bin/activate
exec uvicorn app.main:app --host 127.0.0.1 --port 8000
