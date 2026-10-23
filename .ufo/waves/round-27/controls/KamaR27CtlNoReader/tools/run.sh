#!/usr/bin/env bash
# Variant runner for the round-27 no-reader control seat.
# Usage: run.sh <variant-name> <prepare-script|-> <counter-relative-path> [ENV=VAL ...]
# The prepare script runs after the sandbox tree is reset to the frozen commit
# and before the counter runs. ENV assignments are applied to the counter
# process only (they are NOT applied to the prepare script).
set -u
SB=/fast/scratch/hyaku/kama-r27/KamaR27CtlNoReader
OUT=/tmp/kama-r27-noreader/out
LOCK=/fast/scratch/hyaku/kama-r27/counter.lock
mkdir -p "$OUT"
name="$1"; shift
prep="$1"; shift
counter="$1"; shift

cd "$SB" || exit 9
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE

git checkout -q 530eaa998735d226ec90cea9b0cf4242a6b9cb01 -- .
git clean -qfdx

if [ "$prep" != "-" ]; then
    bash "$prep" "$SB" > "$OUT/$name.prepare.log" 2>&1 || { echo "PREPARE FAILED"; cat "$OUT/$name.prepare.log"; exit 9; }
fi

sha256sum "$counter" > "$OUT/$name.counter.sha256"
sha256sum .ufo/waves/round-27/count-c1.py > "$OUT/$name.frozen-counter.sha256"

if [ "$#" -eq 0 ]; then
    flock "$LOCK" timeout 900 python3 "$counter" --lane . --repo . \
        --out "$OUT/$name.receipt.json" > "$OUT/$name.stdout" 2> "$OUT/$name.stderr"
else
    env "$@" flock "$LOCK" timeout 900 python3 "$counter" --lane . --repo . \
        --out "$OUT/$name.receipt.json" > "$OUT/$name.stdout" 2> "$OUT/$name.stderr"
fi
rc=$?
echo "$rc" > "$OUT/$name.exit"
# snapshot the measured tree so the evidence dir can hold it
T="$OUT/$name.tree"
rm -rf "$T"; mkdir -p "$T"
[ -f registry/error-signatures-r27.json ] && cp registry/error-signatures-r27.json "$T/"
cp SKILL.md "$T/SKILL.md"
cp corpus/SOURCES.md "$T/SOURCES.md"
git diff --stat > "$T/diffstat.txt" 2>/dev/null
git diff > "$T/lane.diff" 2>/dev/null
git status --porcelain > "$T/status.txt" 2>/dev/null
echo "=== variant $name (exit $rc) ==="
cat "$OUT/$name.stdout"
sed -n '1,6p' "$OUT/$name.stderr"
exit 0
