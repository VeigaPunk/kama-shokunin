#!/usr/bin/env bash
# E6: fabricated snapshot + INVENTED literals (same tree as A1)
set -e
python3 /tmp/kama-r27-noreader/mk.py append-block "$1"
python3 /tmp/kama-r27-noreader/gen.py /tmp/kama-r27-noreader/spec_invented.json "$1"
