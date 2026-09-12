#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"
chmod +x ./target-tracker.sh

if ! ./target-tracker.sh 8.8.8.8 --json | grep -Eq '"status"|"target"|"ip"'; then
  echo "FAIL: JSON tracker mode broken"
  exit 1
fi

if ! ./target-tracker.sh --history 2>/dev/null | grep -Eqi 'ASTERIX tracker history|No tracker history'; then
  echo "FAIL: history mode broken"
  exit 1
fi

if ! ./target-tracker.sh 192.168.1.0/24 --sweep 2>/dev/null | grep -Eqi 'ASTERIX sweep mode|\[ONLINE\]|\[DOWN\]'; then
  echo "FAIL: sweep mode broken"
  exit 1
fi

echo "PASS: tracker advanced modes working"
