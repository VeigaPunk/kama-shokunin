#!/usr/bin/env bash
# Canonical captured run for ExecFixtureBoundDemo; writes both the console log and
# nothing else. Guarded per the wave context.
set -u
ulimit -f 1048576 || { echo "GUARD_SET_FAILED"; exit 90; }
ulimit -c 0
OUT=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/w1a3/out/ExecFixtureBoundDemo
cd /fast/scratch/hyaku/kama-r27c/ExecFixtureBoundDemo || exit 91
{
  echo "### canonical captured run $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  timeout 300 bash run-demo.sh
  echo "RUN_DEMO_EXIT=$?"
  timeout 120 bash run-extra.sh
  echo "RUN_EXTRA_EXIT=$?"
  timeout 120 bash run-d3.sh
  echo "RUN_D3_EXIT=$?"
} 2>&1 | tee "$OUT/receipt.log"
echo "PIPE_EXIT=${PIPESTATUS[0]}"
