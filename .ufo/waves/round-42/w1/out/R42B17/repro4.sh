#!/bin/bash
# R42B17 repro 4: fixture repos exercising the counter (tools/round42-digest-audit.py)
S=/fast/scratch/kama-r42/seats/R42B17
export TMPDIR=$S/tmp
CL=$S/clone
CNT=$S/clone/tools/round42-digest-audit.py
mk() { # mk <dir> ; returns via echo
  local D=$1
  rm -rf "$D"; mkdir -p "$D"
  git -C "$D" init -q
  [ "$(git -C "$D" rev-parse --show-toplevel)" = "$D" ] || { echo "TOPLEVEL MISMATCH"; return 1; }
  git -C "$D" config user.email r42b17@fixture.invalid
  git -C "$D" config user.name R42B17
  mkdir -p "$D/tools" "$D/registry"
  git -C "$CL" show 3d9bd8d:tools/digest-ledger.py > "$D/tools/digest-ledger.py"
  git -C "$CL" show 3d9bd8d:SCORECARD.md > "$D/SCORECARD.md"
}

echo "########## F1: hostile ledger row names /etc/shadow (unreadable for uid $(id -u))"
F1=$S/f1; mk "$F1"
T1=2222222222222222222222222222222222222222222222222222222222222222
printf 'digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n%s\texternal\ts\t/etc/shadow\t\t\t\n' "$T1" > "$F1/registry/digest-ledger.tsv"
printf '%s\n' "$T1" > "$F1/doc.md"
git -C "$F1" add -A && git -C "$F1" commit -qm fixture
echo "--- counter on F1 (120 s cap)"
( cd "$F1" && timeout 120 python3 "$CNT" --repo "$F1" --tip HEAD >"$S/f1.out" 2>"$S/f1.err"; echo "exit=$?" )
echo "stdout=[$(head -c 400 "$S/f1.out")]"; echo "stderr_tail=[$(tail -c 400 "$S/f1.err" | tr '\n' '|')]"

echo "########## F2: hostile ledger row names a 4 GiB sparse file (address space capped at 1 GB)"
F2=$S/f2; mk "$F2"
truncate -s 4G "$S/big/huge2.bin"
printf 'digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n%s\texternal\ts\t%s\t\t\t\n' "$T1" "$S/big/huge2.bin" > "$F2/registry/digest-ledger.tsv"
printf '%s\n' "$T1" > "$F2/doc.md"
git -C "$F2" add -A && git -C "$F2" commit -qm fixture
( cd "$F2" && ulimit -v 1000000 && timeout 120 python3 "$CNT" --repo "$F2" --tip HEAD >"$S/f2.out" 2>"$S/f2.err"; echo "exit=$?" )
echo "stdout=[$(head -c 300 "$S/f2.out")]"; echo "stderr_tail=[$(tail -c 300 "$S/f2.err" | tr '\n' '|')]"

echo "########## F3: relative external path -> counter reference and tool resolve against different cwds"
F3=$S/f3; mk "$F3"
printf 'payload\n' > "$F3/ext.bin"; G=$(sha256sum "$F3/ext.bin" | cut -d' ' -f1)
printf 'digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n%s\texternal\ts\text.bin\t\t\t\n' "$G" > "$F3/registry/digest-ledger.tsv"
printf '%s\n' "$G" > "$F3/doc.md"
git -C "$F3" add -A && git -C "$F3" commit -qm fixture
echo "--- tool run the way the counter runs it (cwd = tar export of the tree, no ext.bin):"
EX=$S/f3export; rm -rf "$EX"; mkdir -p "$EX"; git -C "$F3" archive --format=tar HEAD | tar -x -C "$EX"
( cd "$EX" && python3 tools/digest-ledger.py scan --repo "$F3" --rev HEAD; echo "exit=$?" )
echo "--- counter from cwd=$F3 (ref sees ext.bin, tool does not)"
( cd "$F3" && timeout 300 python3 "$CNT" --repo "$F3" --tip HEAD --seed 7 >"$S/f3.out" 2>"$S/f3.err"; echo "exit=$?" )
cat "$S/f3.out"; echo "stderr_tail=[$(tail -c 300 "$S/f3.err" | tr '\n' '|')]"
echo "--- counter from cwd=$S (ref does not see ext.bin either)"
( cd "$S" && timeout 300 python3 "$CNT" --repo "$F3" --tip HEAD --seed 7 >"$S/f3b.out" 2>"$S/f3b.err"; echo "exit=$?" )
cat "$S/f3b.out"
