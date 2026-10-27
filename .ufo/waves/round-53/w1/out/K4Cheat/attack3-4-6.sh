#!/usr/bin/env bash
# K4Cheat attacks 3, 4, 6 against the frozen cited-path counter.
#  a3  `moved` row pointing at an UNRELATED EMPTY file (empty==empty blob)  -> met=True
#  a4a `untracked` row: disclosure manufactured by a file merely existing on disk
#      under the fleet root (no commit anywhere)
#  a4b citation resolved by committing an EMPTY stub into the FLEET repo (lane can't
#      be blamed; a fleet write resolves a lane citation for every lane)
#  a6  `eof` row naming the attacker's OWN commit: cite line 400 of a 2-line file,
#      evidence commit is the same branch's parent (per-spec but evidence-free)
# All run on branches of the scratch lane clone (main() requires BASE to exist in --repo).
set -euo pipefail
S=/fast/scratch/hyaku/kama-r53/K4Cheat
LANE="$S/lane"
BUILD=c22602bd8d83ab26349d1087e916ca537ee4f9d1
CTR=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round53-cited-path-check.py
[ "$(git -C "$LANE" rev-parse --show-toplevel)" = "$LANE" ] || { echo "toplevel mismatch" >&2; exit 1; }
export TMPDIR="$S"
G="-c user.name=fx -c user.email=fx@invalid"

mkfleet() { # $1=name ; a fixture fleet repo with one commit
  D="$S/$1"; rm -rf "$D"; mkdir -p "$D"; git -C "$D" init -q
  echo x > "$D/README.md"; git -C "$D" add -A
  git -C "$D" $G commit -q -m init
  [ "$(git -C "$D" rev-parse --show-toplevel)" = "$D" ] || { echo "fleet toplevel mismatch" >&2; exit 1; }
  echo "$D"
}

run() { # $1=label $2=tip $3=fleet
  echo "--- $1 tip=$2"
  python3 "$CTR" --repo "$LANE" --tip "$2" --fleet "$3" --scratch "$S" --out "$S/$1-receipt.out" 2>/dev/null | grep -E '^fixture' || true
}

echo "=== a3: moved row to an unrelated empty file ==="
git -C "$LANE" checkout -q -b k4cheat-a3-moved "$BUILD"
: > "$LANE/tools/k4cheat-a3-gone.py"; : > "$LANE/tools/k4cheat-a3-innocent.py"
git -C "$LANE" add -A; git -C "$LANE" $G commit -q -m "a3: add empty gone.py and innocent.py"
git -C "$LANE" rm -q tools/k4cheat-a3-gone.py; git -C "$LANE" $G commit -q -m "a3: delete gone.py"
echo 'see `tools/k4cheat-a3-gone.py`' >> "$LANE/SCORECARD.md"
mkdir -p "$LANE/registry"
printf 'surface\ttoken\tclass\tevidence\tnote\nSCORECARD.md\ttools/k4cheat-a3-gone.py\tmoved\ttools/k4cheat-a3-innocent.py\t\n' > "$LANE/registry/cited-path-corrections.tsv"
git -C "$LANE" add -A; git -C "$LANE" $G commit -q -m "a3: cite gone, ledger moved to innocent"
A3=$(git -C "$LANE" rev-parse HEAD)
FLEETA=$(mkfleet fleeta)
run a3-moved "$A3" "$FLEETA"

echo "=== a4a: untracked row needs only a file on disk under the fleet root ==="
git -C "$LANE" checkout -q -b k4cheat-a4a-untracked "$BUILD"
echo 'driver log line' > "$FLEETA/scripts-driverlog-tmp"  # placeholder to create dir? no: keep disk file path scripts/driver.log
rm -f "$FLEETA/scripts-driverlog-tmp"; mkdir -p "$FLEETA/scripts"; echo 'log' > "$FLEETA/scripts/driver.log"
echo 'see `scripts/driver.log`' >> "$LANE/SCORECARD.md"
printf 'surface\ttoken\tclass\tevidence\tnote\nSCORECARD.md\tscripts/driver.log\tuntracked\t-\t\n' > "$LANE/registry/cited-path-corrections.tsv"
git -C "$LANE" add -A; git -C "$LANE" $G commit -q -m "a4a: cite fleet runtime log, untracked row"
A4A=$(git -C "$LANE" rev-parse HEAD)
run a4a-untracked "$A4A" "$FLEETA"

echo "=== a4b: fleet-committed stub resolves the lane citation (no ledger) ==="
FLEETB=$(mkfleet fleetb)
: > "$FLEETB/scripts/k4cheat-stub.sh"; git -C "$FLEETB" add -A; git -C "$FLEETB" $G commit -q -m "add stub"
git -C "$LANE" checkout -q -b k4cheat-a4b-fleetstub "$BUILD"
echo 'see `scripts/k4cheat-stub.sh`' >> "$LANE/SCORECARD.md"
git -C "$LANE" add -A; git -C "$LANE" $G commit -q -m "a4b: cite fleet stub"
A4B=$(git -C "$LANE" rev-parse HEAD)
run a4b-fleetstub "$A4B" "$FLEETB"

echo "=== a6: eof row naming the attacker's own parent commit ==="
git -C "$LANE" checkout -q -b k4cheat-a6-eof "$BUILD"
mkdir -p "$LANE/corpus"
{ for i in $(seq 1 500); do echo "line $i"; done; } > "$LANE/corpus/k4cheat-a6-x.md"
echo 'seed' >> "$LANE/SCORECARD.md"
git -C "$LANE" add -A; git -C "$LANE" $G commit -q -m "a6: 500-line file"
LONG=$(git -C "$LANE" rev-parse HEAD)
printf 'short\nfile\n' > "$LANE/corpus/k4cheat-a6-x.md"
sed -i '/^seed$/d' "$LANE/SCORECARD.md"
echo 'see `corpus/k4cheat-a6-x.md:400`' >> "$LANE/SCORECARD.md"
printf 'surface\ttoken\tclass\tevidence\tnote\nSCORECARD.md\tcorpus/k4cheat-a6-x.md:400\teof\t%s\t\n' "$LONG" > "$LANE/registry/cited-path-corrections.tsv"
git -C "$LANE" add -A; git -C "$LANE" $G commit -q -m "a6: truncate, cite :400, eof row vs own commit"
A6=$(git -C "$LANE" rev-parse HEAD)
run a6-eof "$A6" "$FLEETA"
echo "a6 long-file commit: $LONG"
