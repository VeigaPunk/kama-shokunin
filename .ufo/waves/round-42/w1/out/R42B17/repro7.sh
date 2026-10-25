#!/bin/bash
# R42B17 repro 7: non-UTF-8 tracked doc crashes the counter's reference, tool tolerates it
S=/fast/scratch/kama-r42/seats/R42B17
export TMPDIR=$S/tmp
CL=$S/clone
CNT=$CL/tools/round42-digest-audit.py
D=$(mktemp -d -p /fast/scratch/kama-r42/seats R42B17-u8-XXXX)
exec >>"$S/r7.log" 2>&1
echo "D=$D"
git -C "$D" init -q
top=$(git -C "$D" rev-parse --show-toplevel); echo "toplevel=$top"
[ "$top" = "$D" ] || { echo "TOPLEVEL MISMATCH"; exit 9; }
git -C "$D" config user.email r42b17@fixture.invalid
git -C "$D" config user.name R42B17
mkdir -p "$D/tools" "$D/registry" "$D/corpus"
git -C "$CL" show 3d9bd8d:tools/digest-ledger.py > "$D/tools/digest-ledger.py"
printf '# SCORECARD\n\n**Capabilities - canonical list as of round 42**\n\n| capability | evidence | more |\n|---|---|---|\n| `digest-ledger` | `tools/digest-ledger.py` | x |\n' > "$D/SCORECARD.md"
printf 'digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n' > "$D/registry/digest-ledger.tsv"
printf 'plain ascii doc\n' > "$D/doc.md"
printf 'caf\351 \377\376\n' > "$D/corpus/latin1.md"
git -C "$D" add -A
git -C "$D" commit -qm fixture
git -C "$D" rev-parse --short HEAD
echo "--- tool (git mode) tolerates the non-UTF-8 doc:"
( cd "$D" && python3 tools/digest-ledger.py scan --repo "$D" --rev HEAD; echo "tool_exit=$?" )
echo "--- counter on the same repo:"
( cd "$D" && timeout 300 python3 "$CNT" --repo "$D" --tip HEAD --seed 3 > "$S/r7.out" 2> "$S/r7.err"; echo "counter_exit=$?" )
echo "counter_stdout=[$(cat "$S/r7.out")]"
echo "counter_stderr_tail=[$(tail -c 300 "$S/r7.err" | tr '\n' '|')]"
rm -rf "$D"
echo "===== done"
