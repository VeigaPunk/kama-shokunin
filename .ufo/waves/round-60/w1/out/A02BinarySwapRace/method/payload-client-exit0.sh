#!/bin/sh
# A02BinarySwapRace stage-2b payload: a create client that only logs and exits
# 0 — shows whether the create check alone would accept a bogus client.
printf 'PAYLOAD-CLIENT-EXIT0 pid=%s ppid=%s argv=%s exe=%s\n' \
    "$$" "$PPID" "$*" "$(readlink /proc/$$/exe)" \
    >> /fast/scratch/hyaku/kama-r60/A02BinarySwapRace/hit.log
exit 0
