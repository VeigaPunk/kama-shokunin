#!/usr/bin/env bash
# fixture-dupe3.sh - X2Seven reproduction of the v4 "duplicate head copy" behaviour.
#
# A line born in a dated section, carried byte-identically into an exempt `## Capabilities`
# head, then dropped from the head in a rewrite that keeps the section the same size while
# the dated copy survives. v3 (round-48 tool) leaves all 25 deletions ungraded; v4 grades
# all 25 and reports the event unrestored (exit 1) although every dropped text still exists
# byte-identically in the dated section. This is the mechanism behind the lane's seven
# `## Capabilities` rows at 0718b6ab; there all copies were deleted, so v4's grading is
# restored by 82b5e9d3 rather than a false alarm.
#
# usage: fixture-dupe3.sh <lane clone> <scratch dir>
set -euo pipefail
LANE=${1:?lane clone}
SCR=${2:?scratch dir}
S=$(cd "$SCR" && pwd)
mkdir -p "$S/tool-v3/tools" "$S/tool-v4/tools"
git -C "$LANE" show 438127bc01ff3b99f98468549d58046f932490ef:tools/append-only-audit.py > "$S/tool-v3/tools/append-only-audit.py"
git -C "$LANE" show 74558c71c38ceaeace15fd4cf8aa9d84977584b1:tools/append-only-audit.py > "$S/tool-v4/tools/append-only-audit.py"
D=$(mktemp -d -p "$S" fx-dupe-XXXXXX)
ID=(-c user.name=r49x2-fixture -c user.email=r49x2-fixture@invalid -c commit.gpgsign=false)
git -C "$D" init -q
TOP=$(git -C "$D" rev-parse --show-toplevel)
[ "$(realpath "$TOP")" = "$(realpath "$D")" ] || { echo "fixture toplevel mismatch: $TOP != $D" >&2; exit 2; }
mkdir -p "$D/registry"
printf '%s\n' 'path	rule	declared_at	region	note' \
  'SCORECARD.md	A-corr	SCORE.md:1	exempt=## Capabilities@SCORECARD.md:3	note' > "$D/registry/append-only-contract.tsv"
printf 'SCORECARD.md is append-only\n' > "$D/SCORE.md"
BANNER='The `## Capabilities` head below is re-derived in place.'
rows() { local i; for i in $(seq 0 24); do printf '| dupe row %s born dated | `tools/x.py` | 1%02d |\n' "$i" "$i"; done; }
fresh() { local i; for i in $(seq 0 24); do printf '| fresh row %s | `tools/y.py` | 2%02d |\n' "$i" "$i"; done; }
commit() { git -C "$D" "${ID[@]}" add -A; git -C "$D" "${ID[@]}" commit -q -m "$1"; git -C "$D" rev-parse HEAD; }
{ printf '# s\n\n%s\n\n## Round 1\n' "$BANNER"; rows; } > "$D/SCORECARD.md"
C1=$(commit "seed dated")
{ printf '# s\n\n%s\n\n## Capabilities\n' "$BANNER"; rows; printf '\n## Round 1\n'; rows; } > "$D/SCORECARD.md"
C2=$(commit "carry rows into the exempt head")
{ printf '# s\n\n%s\n\n## Capabilities\n' "$BANNER"; fresh; printf '\n## Round 1\n'; rows; } > "$D/SCORECARD.md"
C3=$(commit "head rewrite drops the carried rows")
git -C "$D" diff "$C2" "$C3" > "$S/fixture-dupe3-c3.diff"
echo "fixture $D c1=$C1 c2=$C2 c3=$C3"
for v in v3 v4; do
  set +e
  out=$(python3 "$S/tool-$v/tools/append-only-audit.py" --repo "$D" --to "$C3" --json); rc=$?
  set -e
  V=$v RC=$rc OUT=$out python3 - <<'PY'
import json,os
v,rc=os.environ["V"],int(os.environ["RC"])
j=json.loads(os.environ["OUT"])
print(f"{v} exit {rc} definition {j.get('definition')} decls_ok {[d['ok'] for d in j['declarations']]}")
for e in j["events"]:
    print(f"  {v} event {e['commit'][:8]} deleted {e['deleted']} graded {e['graded']} ungraded {e['ungraded']} "
          f"restored_max {e['restored_max']} held_at_to {e['held_at_to']} status {e['status']}")
PY
done
