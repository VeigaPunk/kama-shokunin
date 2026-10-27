#!/bin/sh
for a in "$@"; do
  case "$a" in
    show) mod=show ;;
    rev-parse) mod=rev ;;
  esac
done
if [ "$mod" = rev ]; then
  printf 'efc6b3ec6fb6ea308c15855e9b8b62856f4255b7\n'
  exit 0
fi
case "$*" in
  *preregistration.json) cat <<'JSON'
{"battery": {"roster": {"a": {"designation": "kill", "expected": "missed"}, "b": {"designation": "control", "expected": "missed"}, "c": {"designation": "positive-control", "expected": "detected"}}}}
JSON
  ;;
  *env-leg-battery.py) cat <<'PY'
ROSTER = {"a": {"designation": "kill", "expected": "missed"}, "b": {"designation": "control", "expected": "missed"}, "c": {"designation": "positive-control", "expected": "detected"}}
PY
  ;;
  *) exit 128 ;;
esac
exit 0
