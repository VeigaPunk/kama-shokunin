#!/usr/bin/env bash
# A1: fabricated source snapshot (pinned file edited to hold INVENTED literals)
set -e
python3 /tmp/kama-r27-noreader/mk.py append-block "$1"
python3 /tmp/kama-r27-noreader/gen.py /tmp/kama-r27-noreader/spec_invented.json "$1"
