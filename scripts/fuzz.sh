#!/usr/bin/env bash
# Runs adaptive, coverage-guided continuous fuzzing on property-based tests using HypoFuzz.

set -euo pipefail

echo "Starting HypoFuzz continuous fuzzing on tests/test_properties.py..."
exec uv run hypothesis fuzz tests/test_properties.py "$@"
