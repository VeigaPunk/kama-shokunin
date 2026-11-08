#!/usr/bin/env bash
# Re-run only the round-89 harm counter for the given mutants (94 already recorded).
set -u
ROOT=/fast/scratch/hyaku/kama-r94/MT01ProbeMutants
REPO=/home/vgpnk/Projects/shokunin/kama-shokunin
REV=a27656a454b1a2364f8b6e55f42fbca8c2e86ee4
export TMPDIR="$ROOT/tmp"
# Isolation: a sibling wrote ggml-org/embeddinggemma-300M-qat-q4_0-GGUF into the shared HF
# cache at 00:11, so the pinned router lists a cache-sourced model whose args are not under
# the run's private dir and the counter aborts (rc=2) on its own identity guard. Point the
# child's cache at empty dirs; the operator's cache files are left untouched.
export LLAMA_CACHE="$ROOT/cache-empty"
export HF_HOME="$ROOT/hf-home"
mkdir -p "$TMPDIR" "$ROOT/logs" "$ROOT/w89" "$LLAMA_CACHE" "$HF_HOME"
for m in "$@"; do
  P="$ROOT/mutants/$m/kama-probe.sh"
  for attempt in 1 2 3; do
    python3 "$REPO/tools/round89-unloadable-cells.py" --repo "$REPO" --rev "$REV" \
      --work "$ROOT/w89/$m-$attempt" --probe-file "$P" \
      > "$ROOT/logs/$m-89-try$attempt.out" 2>&1
    rc=$?
    echo "## exit=$rc attempt=$attempt load=$(cut -d' ' -f1 /proc/loadavg)" >> "$ROOT/logs/$m-89-try$attempt.out"
    echo "-- $m 89 try$attempt rc=$rc $(tail -2 "$ROOT/logs/$m-89-try$attempt.out" | tr '\n' '|')"
    [ "$rc" != 2 ] && break
    sleep 5
  done
done
echo "ALL DONE $(date -Is)"
