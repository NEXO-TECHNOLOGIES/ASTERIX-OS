#!/usr/bin/env bash
set -e

SCRIPT_PATH="${1:-$(cd "$(dirname "$0")" && pwd)/asterix-ai-startup.sh}"

if [ ! -f "$SCRIPT_PATH" ]; then
  echo "FAIL: asterix-ai-startup.sh is missing"
  exit 1
fi

if ! bash "$SCRIPT_PATH" > /tmp/asterix_ai_boot_test.out 2>&1; then
  echo "FAIL: startup script exited with a non-zero status"
  exit 1
fi

if ! grep -Eqi "ASTERIX AI|startup|background|ready" /tmp/asterix_ai_boot_test.out; then
  echo "FAIL: startup script did not emit boot AI status"
  exit 1
fi

echo "PASS: startup AI helper boots correctly"
rm -f /tmp/asterix_ai_boot_test.out
