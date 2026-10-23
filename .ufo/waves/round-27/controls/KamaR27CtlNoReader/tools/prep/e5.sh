#!/usr/bin/env bash
# E5: rows citing REAL 704366d literals, fabricated triggers; pinned snapshot untouched
set -e
python3 /tmp/kama-r27-noreader/gen.py /tmp/kama-r27-noreader/spec_real.json "$1"
