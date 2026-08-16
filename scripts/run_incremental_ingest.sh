#!/usr/bin/env bash
set -euo pipefail
cd /home/andres/threat-hunter
source .venv/bin/activate
python scripts/ingest_obsidian_incremental.py >> /home/andres/threat-hunter/logs/ingest.log 2>&1
