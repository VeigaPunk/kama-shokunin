#!/usr/bin/env bash
# Phase A: round-89 harm counter for the remaining mutants (isolated cache).
# Phase B: round-94 counter for the mutants whose earlier attempts hit the counter's own
#          environment guard ("fixture slow.gguf: base loader state '-'"), gated on the host
#          load falling back under 200 (the counter cannot evaluate its own fixture above that).
set -u
ROOT=/fast/scratch/hyaku/kama-r94/MT01ProbeMutants
REPO=/home/vgpnk/Projects/shokunin/kama-shokunin
REV=a27656a454b1a2364f8b6e55f42fbca8c2e86ee4
export TMPDIR="$ROOT/tmp"
export LLAMA_CACHE="$ROOT/cache-empty"
export HF_HOME="$ROOT/hf-home"
mkdir -p "$TMPDIR" "$ROOT/logs" "$ROOT/w89" "$ROOT/w94" "$LLAMA_CACHE" "$HF_HOME"

for m in M05 M08 M09 M10 M11 M12 M14; do
  P="$ROOT/mutants/$m/kama-probe.sh"
  for attempt in 1 2 3; do
    python3 "$REPO/tools/round89-unloadable-cells.py" --repo "$REPO" --rev "$REV" \
      --work "$ROOT/w89/$m-a$attempt" --probe-file "$P" \
      > "$ROOT/logs/$m-89-try$attempt.out" 2>&1
    rc=$?
    echo "## exit=$rc attempt=$attempt load=$(cut -d' ' -f1 /proc/loadavg)" >> "$ROOT/logs/$m-89-try$attempt.out"
    echo "-- $m 89 try$attempt rc=$rc $(tail -2 "$ROOT/logs/$m-89-try$attempt.out" | tr '\n' '|')"
    [ "$rc" != 2 ] && break
    sleep 5
  done
done

echo "== phase B: waiting for load1 < 200 $(date -Is)"
for _ in $(seq 1 60); do
  l1=$(cut -d' ' -f1 /proc/loadavg)
  awk -v v="$l1" 'BEGIN{exit !(v+0 < 200)}' && break
  sleep 30
done
echo "== phase B start $(date -Is) load=$(cut -d' ' -f1 /proc/loadavg)"

for m in M02 M05 M11 M12 M14; do
  P="$ROOT/mutants/$m/kama-probe.sh"
  for attempt in 1 2 3 4; do
    python3 "$REPO/tools/round94-router-budget.py" --repo "$REPO" --rev "$REV" \
      --work "$ROOT/w94/$m-b$attempt" --probe-file "$P" --burners 32 --runs 1 \
      > "$ROOT/logs/$m-94-tryb$attempt.out" 2>&1
    rc=$?
    echo "## exit=$rc attempt=$attempt load=$(cut -d' ' -f1 /proc/loadavg)" >> "$ROOT/logs/$m-94-tryb$attempt.out"
    echo "-- $m 94 tryB$attempt rc=$rc $(tail -2 "$ROOT/logs/$m-94-tryb$attempt.out" | tr '\n' '|')"
    [ "$rc" != 2 ] && break
    sleep 30
  done
done
echo "ALL DONE $(date -Is)"
