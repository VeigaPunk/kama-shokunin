#!/bin/sh
# A02BinarySwapRace stage-2 payload: proves a non-pinned program ran as the
# create client, then delegates to the real pinned binary so the create the
# server sees is genuine.
printf 'PAYLOAD-CLIENT pid=%s ppid=%s argv=%s exe=%s\n' \
    "$$" "$PPID" "$*" "$(readlink /proc/$$/exe)" \
    >> /fast/scratch/hyaku/kama-r60/A02BinarySwapRace/hit.log
exec /fast/scratch/hyaku/kama-r60/A02BinarySwapRace/pinbin "$@"
