#!/bin/sh
# run_counter.sh CLONE_DIR MUTANT_FILE TIP
# Commit MUTANT_FILE as tools/append-only-audit.py on top of TIP inside CLONE_DIR
# (a disposable --shared clone), run the frozen C2 counter on that commit.
set -u
CLONE="$1"; MUT="$2"; TIP="$3"
S=/fast/scratch/hyaku/kama-r50/M3Tool
B=$(basename "$MUT" .py)

top=$(git -C "$CLONE" rev-parse --show-toplevel) || exit 98
[ "$top" = "$CLONE" ] || { echo "$B TOPLEVEL-MISMATCH $top"; exit 98; }
case "$top" in /fast/scratch/hyaku/kama-r50/M3Tool/*) ;; *) echo "$B OUT-OF-SCRATCH $top"; exit 98;; esac

git -C "$CLONE" checkout -q --detach "$TIP" || exit 98
cp "$MUT" "$CLONE/tools/append-only-audit.py"
git -C "$CLONE" add tools/append-only-audit.py
SHA=$(git -C "$CLONE" -c user.name=m3tool -c user.email=m3tool@invalid -c commit.gpgsign=false \
      commit -q -m "mutant $B" && git -C "$CLONE" rev-parse HEAD)
SHA=$(git -C "$CLONE" rev-parse HEAD)
mkdir -p "$S/c2out"
out=$(TMPDIR="$S" timeout 600 python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round50-append-audit-v5-check.py \
      --repo "$CLONE" --tip "$SHA" --scratch "$S/c2s-$B" --out "$S/c2out/$B.receipt" 2>&1)
rc=$?
printf '%s rc=%s :: %s\n' "$B" "$rc" "$(printf '%s' "$out" | grep -E '^(fixture=|could-not)' | head -1)"
printf '%s' "$out" | grep -E 'FAIL|<= v5|!=|does not|unreadable|absent' | head -4 | sed "s/^/    $B /"
git -C "$CLONE" checkout -q --detach "$TIP"
