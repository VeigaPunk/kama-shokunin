#!/usr/bin/env bash
# E02CanonicalBinding - run every prototype control and record exact exits.
# Writes receipts/<name>.out with the tool's stdout and exits/<name>.exit.
set -u
SEAT=/fast/scratch/hyaku/kama-r57/E02CanonicalBinding
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
CTRL=$LANE/.ufo/waves/round-57/controls
cd "$SEAT" || exit 2
mkdir -p receipts exits
run() { # run <name> <cmd...>
  local name=$1; shift
  "$@" > "receipts/$name.out" 2>&1
  echo $? > "exits/$name.exit"
  printf '%-24s exit=%s  %s\n' "$name" "$(cat "exits/$name.exit")" "$(tail -1 "receipts/$name.out")"
}

# --- instrument: genuine canonical table at the frozen base -------------------
run genuine-base python3 canon-binding.py audit --repo "$LANE" --tip b89bdab2 --scratch ./tmp

# --- forgeries built from the genuine output (controls for verify) -----------
python3 - "$SEAT" <<'PY'
import sys
seat = sys.argv[1]
genuine = open(f"{seat}/receipts/genuine-base.out").read()
# (a) one digest flipped: the shape is right, the bytes are not
forged = genuine.replace("canon_sha256=e27664aa", "canon_sha256=f27664aa", 1)
open(f"{seat}/receipts/forged-sha.out", "w").write(forged)
# (b) summary intact, every per-row binding line dropped: a no-op that keeps counts
kept = [l for l in genuine.split("\n") if not l.startswith("row=")]
open(f"{seat}/receipts/forged-omit.out", "w").write("\n".join(kept))
PY

# --- instrument: omission fixtures shipped with the round-57 freeze -----------
run noop-rows-only python3 canon-binding.py audit --root "$CTRL/canonical-noop" --scratch ./tmp
run no-canonical   python3 canon-binding.py audit --root "$CTRL/no-canonical" --scratch ./tmp

# --- instrument: content / execution mutations on the base tree --------------
run mut-exec    python3 canon-binding.py audit --root fixtures/mut-exec    --scratch ./tmp
run mut-silent  python3 canon-binding.py audit --root fixtures/mut-silent  --scratch ./tmp
run mut-delete  python3 canon-binding.py audit --root fixtures/mut-delete  --scratch ./tmp
run mut-stale   python3 canon-binding.py audit --root fixtures/mut-stale   --scratch ./tmp

# --- verify: the instrument's own genuine output is accepted -----------------
run verify-genuine   python3 canon-binding.py verify --repo "$LANE" --tip b89bdab2 --scratch ./tmp --instrument-out receipts/genuine-base.out

# --- verify: no-op / forged / stale / omitted-row instruments are rejected ---
# frozen control receipts are read from the commit that froze them (7c873d7b):
# the worktree copies moved after the freeze, so the commit is the stable source.
mkdir -p frozen
for f in noop-c1.out noop-c2.out c1-noop.py freeze.txt; do
  git -C "$LANE" show 7c873d7b:.ufo/waves/round-57/controls/$f > "frozen/$f"
done
python3 frozen/c1-noop.py > receipts/frozen-noop.out 2>&1; echo $? > exits/frozen-noop.exit
run verify-frozen-noop python3 canon-binding.py verify --repo "$LANE" --tip b89bdab2 --scratch ./tmp --instrument-out receipts/frozen-noop.out
run verify-frozen-noop-c2-receipt python3 canon-binding.py verify --repo "$LANE" --tip b89bdab2 --scratch ./tmp --instrument-out frozen/noop-c2.out
run verify-frozen-noop-c1-receipt python3 canon-binding.py verify --repo "$LANE" --tip b89bdab2 --scratch ./tmp --instrument-out frozen/noop-c1.out
run verify-base-as-if-noop-rows python3 canon-binding.py verify --repo "$LANE" --tip b89bdab2 --scratch ./tmp --instrument-out receipts/noop-rows-only.out
run verify-stale-table python3 canon-binding.py verify --repo "$LANE" --tip b89bdab2 --scratch ./tmp --instrument-out receipts/mut-stale.out
run verify-forged-sha python3 canon-binding.py verify --repo "$LANE" --tip b89bdab2 --scratch ./tmp --instrument-out receipts/forged-sha.out
run verify-forged-omit python3 canon-binding.py verify --repo "$LANE" --tip b89bdab2 --scratch ./tmp --instrument-out receipts/forged-omit.out

# --- audit the fixture trees that the verify rejections above refer to ------
run verify-noop-rows-against-fixture python3 canon-binding.py verify --root "$CTRL/canonical-noop" --scratch ./tmp --instrument-out receipts/genuine-base.out

# --- nonce-bound invocation: the instrument is run afresh, not read from a file ---
run verify-cmd-genuine python3 canon-binding.py verify --repo "$LANE" --tip b89bdab2 --scratch ./tmp --instrument-cmd "python3 $SEAT/canon-binding.py audit --repo $LANE --tip b89bdab2 --scratch $SEAT/tmp"
run verify-cmd-noop python3 canon-binding.py verify --repo "$LANE" --tip b89bdab2 --scratch ./tmp --instrument-cmd "python3 $SEAT/noop-instrument.py"
run verify-cmd-copycat-sametip python3 canon-binding.py verify --repo "$LANE" --tip b89bdab2 --scratch ./tmp --instrument-cmd "python3 $SEAT/copycat-instrument.py"
run verify-cmd-copycat-othertree python3 canon-binding.py verify --root fixtures/mut-extra-row --scratch ./tmp --instrument-cmd "python3 $SEAT/copycat-instrument.py"

# --- table-driven row set: the input is the canonical table, not a constant -----
run mut-extra-row python3 canon-binding.py audit --root fixtures/mut-extra-row --scratch ./tmp
run mut-rename   python3 canon-binding.py audit --root fixtures/mut-rename   --scratch ./tmp
run mut-empty    python3 canon-binding.py audit --root fixtures/mut-empty    --scratch ./tmp
run no-heading   python3 canon-binding.py audit --root fixtures/no-heading   --scratch ./tmp
run verify-mut-extra-row python3 canon-binding.py verify --repo "$LANE" --tip b89bdab2 --scratch ./tmp --instrument-out receipts/mut-extra-row.out
run verify-mut-rename    python3 canon-binding.py verify --repo "$LANE" --tip b89bdab2 --scratch ./tmp --instrument-out receipts/mut-rename.out
