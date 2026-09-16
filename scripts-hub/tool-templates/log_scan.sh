#!/usr/bin/env bash
set -u

USAGE="Usage: $(basename "$0") [--path PATH] [--pattern PATTERN] [--json]"
PATH_TO_SCAN="/var/log"
PATTERN="error"
JSON_OUT=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --path)
      PATH_TO_SCAN="$2"
      shift 2
      ;;
    --pattern)
      PATTERN="$2"
      shift 2
      ;;
    --json)
      JSON_OUT=true
      shift
      ;;
    -h|--help)
      echo "$USAGE"
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      echo "$USAGE" >&2
      exit 2
      ;;
  esac
done

if [[ "$JSON_OUT" == true ]]; then
  printf '{\n  "path": "%s",\n  "pattern": "%s",\n  "matches": [' "$PATH_TO_SCAN" "$PATTERN"
  first=true
  while IFS= read -r line; do
    if [[ "$line" =~ $PATTERN ]]; then
      if [[ "$first" == true ]]; then
        first=false
      else
        printf ',\n'
      fi
      printf '    %s' "$(printf '%s' "$line" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().rstrip("\n")))')"
    fi
  done < <(grep -R -n -E "$PATTERN" "$PATH_TO_SCAN" 2>/dev/null)
  printf '\n  ]\n}\n'
else
  grep -R -n -E "$PATTERN" "$PATH_TO_SCAN" 2>/dev/null || true
fi
