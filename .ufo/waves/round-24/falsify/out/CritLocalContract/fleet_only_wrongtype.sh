#!/usr/bin/env bash
# Benign offline fixture: a Landed citation that names a locally present,
# non-commit object held only by the second audited store (the fleet).
# Usage: fleet_only_wrongtype.sh AUDITOR SCRATCH
set -u
AUD=$1; S=$2
rm -rf "$S/fx"; mkdir -p "$S/fx"; cd "$S/fx" || exit 9
export TMPDIR=$S/tmp GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
g() { git -c user.name=kama-shokunin -c user.email=k@x -c init.defaultBranch=master "$@"; }
mk() { # repo when msg file content
  printf '%s' "$5" > "$1/$4"; g -C "$1" add "$4"
  GIT_AUTHOR_DATE="$2 +0000" GIT_COMMITTER_DATE="$2 +0000" g -C "$1" commit -qm "$3"; }

g init -q lane; g init -q fleet
mk lane 1700000000 "round-1: lane work" f "lane content"
LANE_SHA=$(git -C lane rev-parse HEAD)
LANE_BLOB=$(git -C lane rev-parse HEAD:f)
mk fleet 1700000100 "fleet other" other.txt "fleet-only content"
FLEET_BLOB=$(git -C fleet rev-parse HEAD:other.txt)
FLEET_TREE=$(git -C fleet rev-parse HEAD^{tree})
mkdir -p fleet/.ufo/reports/round-1
run() { # label report-cited-token [errata-file]
  printf '# r1\n\n## Landed changes\n\n- %s\n- %s\n' "$LANE_SHA" "$2" \
    > fleet/.ufo/reports/round-1/kama.md
  g -C fleet add .ufo/reports/round-1/kama.md
  GIT_AUTHOR_DATE="1700000200 +0000" GIT_COMMITTER_DATE="1700000200 +0000" \
    g -C fleet commit -qm "report $1" --allow-empty
  local extra=(--no-errata); [ -n "${3:-}" ] && extra=(--errata "$3")
  python3 "$AUD" --lane-repo lane --fleet-repo fleet --branch master \
    --rounds 1 "${extra[@]}" --json > "$S/out-$1.json" 2> "$S/err-$1.txt"
  echo "CASE $1 token=$2 exit=$?"
  head -c 400 "$S/err-$1.txt"; echo
  python3 - "$S/out-$1.json" <<'PY'
import json,sys
try: d=json.load(open(sys.argv[1]))
except Exception: print("  no JSON verdict"); sys.exit()
print("  status", d["summary"]["status"], [(x["kind"], x["token"][:12]) for r in d["results"] for x in r["defects"]],
      "invalid", [e["correction"][:12] for e in d["errata_invalid"]])
PY
}
run lane-blob-control "$LANE_BLOB"
run fleet-blob "$FLEET_BLOB"
run fleet-tree "$FLEET_TREE"
run fleet-blob-abbrev "${FLEET_BLOB:0:12}"
printf '1\tlanded-unresolved\t%s\t%s\tev\n' "$LANE_BLOB" "$LANE_BLOB" > "$S/errata-lane.tsv"
printf '1\tlanded-unresolved\t%s\t%s\tev\n' "$FLEET_BLOB" "$FLEET_BLOB" > "$S/errata-fleet.tsv"
run errata-lane-blob-correction "$LANE_BLOB" "$S/errata-lane.tsv"
run errata-fleet-blob-correction "$FLEET_BLOB" "$S/errata-fleet.tsv"
printf '1\tlanded-unresolved\t%s\t%s\tev\n' "$LANE_BLOB" "$FLEET_BLOB" > "$S/errata-mixed.tsv"
run errata-lane-defect-fleet-blob-correction "$LANE_BLOB" "$S/errata-mixed.tsv"
echo "missing-sets:"; for r in lane fleet; do
  printf '%s ' $r; git -C $r rev-list --objects --missing=print --all | grep -c '^?'; done
