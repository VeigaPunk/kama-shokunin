#!/usr/bin/env bash
# A2: fabricated UNPINNED extra source file, rows cite it
set -e
python3 /tmp/kama-r27-noreader/mk.py extra-file "$1"
python3 /tmp/kama-r27-noreader/mk.py spec-extra /tmp/kama-r27-noreader/spec_extra.json
python3 /tmp/kama-r27-noreader/gen.py /tmp/kama-r27-noreader/spec_extra.json "$1"
