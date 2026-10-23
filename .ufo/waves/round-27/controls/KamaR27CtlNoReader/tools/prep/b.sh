#!/usr/bin/env bash
# B: mutant counter copy (fake server + rewritten pins) over the fabricated tree
set -e
python3 /tmp/kama-r27-noreader/mk.py append-block "$1"
python3 /tmp/kama-r27-noreader/gen.py /tmp/kama-r27-noreader/spec_invented.json "$1"
python3 /tmp/kama-r27-noreader/mk.py mutant "$1" "$1/.ufo/waves/round-27/count-c1.MUTANT-fake-server.py"
