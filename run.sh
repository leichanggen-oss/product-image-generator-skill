#!/usr/bin/env bash
set -euo pipefail
python scripts/generate.py examples/cold-plunge/product-oval.yaml "$@"
