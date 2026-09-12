#!/usr/bin/env bash
set -e

SCRIPT_PATH="${1:-$(cd "$(dirname "$0")" && pwd)/target-tracker.sh}"

if [ ! -f "$SCRIPT_PATH" ]; then
  echo "FAIL: target-tracker.sh is missing"
  exit 1
fi

OUTPUT_FILE="$(mktemp)"
if ! bash "$SCRIPT_PATH" 8.8.8.8 > "$OUTPUT_FILE" 2>&1; then
  echo "FAIL: target-tracker.sh exited with a non-zero status"
  exit 1
fi

if ! grep -Eqi "TARGET|IP.*8\.8\.8\.8|STATUS|TIME" "$OUTPUT_FILE"; then
  echo "FAIL: tracker output did not contain expected IP metadata"
  exit 1
fi

echo "PASS: target tracker emits target metadata"
rm -f "$OUTPUT_FILE"
