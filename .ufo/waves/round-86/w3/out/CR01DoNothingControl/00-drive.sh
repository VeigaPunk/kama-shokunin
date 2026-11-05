#!/usr/bin/env bash
# CR01DoNothingControl receipt driver. cwd = clone at bafae7af.
set -u
COPY=/fast/scratch/hyaku/kama-r86/CR01DoNothingControl/copy
OUT=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-86/w3/out/CR01DoNothingControl
mkdir -p "$OUT" "$COPY/w/rec"
cd "$COPY"

run() { # run <receipt> <label> <command...>
  local rec="$OUT/$1"; shift
  local label="$1"; shift
  { echo "=== $label"; echo "\$ $*"; "$@"; echo "exit=$?"; } > "$rec" 2>&1
}

git checkout -- tools/round86-rendered-cells.py tools/round86-mutant-owners.py tools/round86-pin-origin.py tools/round81-append-debt.py
{
  echo "seat=CR01DoNothingControl round=86 wave=w3"
  echo "date=$(date -Is)"
  echo "host=$(uname -srm)"
  echo "python=$(python3 -VV 2>&1)"
  echo "clone=$(git rev-parse --show-toplevel) HEAD=$(git rev-parse HEAD)"
  echo "target_tip=bafae7afb41843564ac2468d28beb8e0bb98e8e6 base=3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d freeze=c07e1f909414aafb2d8de5605a81fd3bd4e3550e"
  echo "--- worktree instrument sha256 (clean) ---"
  sha256sum tools/round86-rendered-cells.py tools/round86-mutant-owners.py tools/round86-pin-origin.py .ufo/waves/round-86/count.py
  echo "--- counter execution line ---"
  grep -n 'sys.executable' .ufo/waves/round-86/count.py
  echo "--- counter bytes unchanged c07e1f90..bafae7af ---"
  git diff --stat c07e1f90 bafae7af -- .ufo/waves/round-86/count.py; echo "(empty = frozen)"
} > "$OUT/00-env.receipt" 2>&1

run 01-c1-before-replay.out "C1 before control replayed at base 3ff23da3" \
  python3 .ufo/waves/round-86/count.py c1 --repo "$COPY" --rev 3ff23da3 --work "$COPY/w/rec/c1b"
run 02-c2-before-replay.out "C2 before control replayed at base 3ff23da3" \
  python3 .ufo/waves/round-86/count.py c2 --repo "$COPY" --rev 3ff23da3 --work "$COPY/w/rec/c2b"
run 03-c3-before-replay.out "C3 before control replayed at base 3ff23da3" \
  python3 .ufo/waves/round-86/count.py c3 --repo "$COPY" --rev 3ff23da3 --work "$COPY/w/rec/c3b"
run 04-c1-record.out "C1 at the graded tip bafae7af" \
  python3 .ufo/waves/round-86/count.py c1 --repo "$COPY" --rev bafae7af --work "$COPY/w/rec/c1h"
run 05-c2-record.out "C2 at the graded tip bafae7af" \
  python3 .ufo/waves/round-86/count.py c2 --repo "$COPY" --rev bafae7af --work "$COPY/w/rec/c2h"
run 06-c3-record-live.out "C3 at the graded tip bafae7af (live upstream fetch)" \
  python3 .ufo/waves/round-86/count.py c3 --repo "$COPY" --rev bafae7af --work "$COPY/w/rec/c3h"

# freeze instrument (c07e1f90) against the repaired record: C1 target reachable with zero instrument work
git show c07e1f90:tools/round86-rendered-cells.py > w/freeze/round86-rendered-cells.py
git show c07e1f90:tools/round86-mutant-owners.py > w/freeze/round86-mutant-owners.py
run 07-c1-freeze-instrument-at-record.out "C1 freeze instrument (c07e1f90) on bafae7af bytes" \
  python3 w/freeze/round86-rendered-cells.py --repo "$COPY" --rev bafae7af
run 08-c1-two-line-fixture.out "C1 do-nothing fixture: base tree + only SCORECARD lines 6 and 18 (fixture $(cat w/fixture-c1.txt))" \
  python3 w/freeze/round86-rendered-cells.py --repo "$COPY" --rev "$(cat w/fixture-c1.txt)"
run 09-c2-freeze-instrument-at-record.out "C2 freeze instrument (c07e1f90) on bafae7af bytes" \
  python3 w/freeze/round86-mutant-owners.py --repo "$COPY" --rev bafae7af --work "$COPY/w/rec/f2"
run 10-c2-one-print-fixture.out "C2 do-nothing fixture: base tree + ONE ARMS print line, no assertion (fixture $(cat w/fixture-c2.txt))" \
  python3 tools/round86-mutant-owners.py --repo "$COPY" --rev "$(cat w/fixture-c2.txt)" --work "$COPY/w/rec/f2b"

# tampered-worktree green-at-base demonstrations
cp w/stub_c1.py tools/round86-rendered-cells.py
cp w/stub_c2.py tools/round86-mutant-owners.py
cp w/stub_c3.py tools/round86-pin-origin.py
{ echo "=== tampered worktree instrument sha256"; sha256sum tools/round86-rendered-cells.py tools/round86-mutant-owners.py tools/round86-pin-origin.py; } > "$OUT/11-tamper-preamble.out"
run 12-T1-c1-green-at-base.out "T1 C1 tampered worktree, --rev 3ff23da3" \
  python3 .ufo/waves/round-86/count.py c1 --repo "$COPY" --rev 3ff23da3 --work "$COPY/w/rec/t1"
run 13-T2-c2-green-at-base.out "T2 C2 tampered worktree, --rev 3ff23da3" \
  python3 .ufo/waves/round-86/count.py c2 --repo "$COPY" --rev 3ff23da3 --work "$COPY/w/rec/t2"
run 14-T3-c3-green-at-record.out "T3 C3 tampered worktree, --rev bafae7af, no network" \
  python3 .ufo/waves/round-86/count.py c3 --repo "$COPY" --rev bafae7af --work "$COPY/w/rec/t3"
run 15-T4-c3-presence-gate.out "T4 C3 tampered worktree, --rev 3ff23da3 (presence gate reads the rev)" \
  python3 .ufo/waves/round-86/count.py c3 --repo "$COPY" --rev 3ff23da3 --work "$COPY/w/rec/t4"
run 16-T5-c3-green-at-base-fixture.out "T5 C3 tampered worktree, --rev fixture $(cat w/fixture-c3.txt) = base tree + stub at the instrument path" \
  python3 .ufo/waves/round-86/count.py c3 --repo "$COPY" --rev "$(cat w/fixture-c3.txt)" --work "$COPY/w/rec/t5"

git checkout -- tools/round86-rendered-cells.py tools/round86-mutant-owners.py tools/round86-pin-origin.py
{ echo "=== worktree instrument sha256 (restored)"; sha256sum tools/round86-rendered-cells.py tools/round86-mutant-owners.py tools/round86-pin-origin.py; } > "$OUT/17-restored.out"

run 18-selftests.out "frozen instrument selftests at bafae7af" bash -c 'for t in rendered-cells mutant-owners pin-origin; do echo "--- $t"; python3 tools/round86-$t.py --selftest; echo "rc=$?"; done'
run 19-c1-mutants.out "C1 source-mutant driver at bafae7af" env TMPDIR="$COPY/w/rec/mut" python3 .ufo/waves/round-86/measured/after/c1-mutants.py "$COPY"

{
  echo "=== record-number audit against committed bytes"
  echo "--- SCORECARD C1 says 10 mutants; lesson M3 says 7/7:"
  git show bafae7af:SCORECARD.md | grep -o '10 source mutants each killed by a named arm'
  git show bafae7af:corpus/lessons/round-86.md | grep -n '7/7 source mutants'
  echo "--- committed driver declares N mutants:"
  git show bafae7af:.ufo/waves/round-86/measured/after/c1-mutants.py | grep -c '^    "[a-z0-9-]*": ('
  echo "--- committed receipt:"
  git show bafae7af:.ufo/waves/round-86/measured/after/c1-mutants.out | tail -2
  echo "--- worktree-landing arm default paths (round-86 instruments are NOT among them):"
  sed -n '42,48p' tools/round67-worktree-landing-check.py
  echo "--- gate receipt's landing arm (ec541687, after the terminal measurement):"
  git show master:.ufo/waves/round-86/measured/terminal/gate.out | grep 'worktree-landing'
  echo "--- SOURCES row count at bafae7af (record claims 319):"
  git show bafae7af:corpus/SOURCES.md | grep -cE '^\| *S[0-9]{3}'
  echo "--- append-only-late rows added base..tip (record claims 15):"
  git diff 3ff23da3 bafae7af -- registry/append-only-late.tsv | grep -c '^+[^+]'
} > "$OUT/20-record-number-audit.out" 2>&1

echo done
