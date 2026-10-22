#!/usr/bin/env bash
# Verbatim command/exit/finding transcripts for the decisive cases.
set -u
T=/fast/scratch/hyaku/kama-r24/falsify/CodeStatusPriority
OUT=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CodeStatusPriority
TMPDIR=$T
export TMPDIR
for c in A-blob-in-lane-only B-blob-in-fleet-only C-control-no-blob-citation \
         D-tag-lane-conclusive E-tag-lane-unknown \
         F-errata-fleet-only-blob G-errata-lane-blob \
         H-cross-repo-found I-tag-both-missing; do
  W=$T/work/cli-$c
  echo "### $c"
  echo "\$ python3 $T/tools/report-landing-audit.py --lane-repo $W/lane --fleet-repo $W/fleet --branch master --lane kama --rounds 24 --json"
  python3 $T/tools/report-landing-audit.py --lane-repo "$W/lane" --fleet-repo "$W/fleet" \
      --branch master --lane kama --rounds 24 --json > "$OUT/.stdout" 2> "$OUT/.stderr"
  echo "exit=$?"
  if [ -s "$OUT/.stderr" ]; then echo "stderr: $(cat "$OUT/.stderr")"; fi
  python3 - "$OUT/.stdout" <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception as exc:
    print("stdout: (unparsable)", exc)
    raise SystemExit(0)
print("status:", d["summary"]["status"],
      "defects:", [(x["kind"], x["token"]) for r in d["results"] for x in r["defects"]],
      "errata_invalid:", d["summary"]["errata_invalid"],
      "errata_unmatched:", d["summary"]["errata_unmatched"])
PY
  echo
done
for c in A-blob-in-lane-only B-blob-in-fleet-only; do
  W=$T/work/base-$c
  echo "### r23-base-$c (base 0df800e)"
  echo "\$ python3 $T/base/report-landing-audit.py --lane-repo $W/lane --fleet-repo $W/fleet --branch master --lane kama --rounds 24 --json"
  python3 $T/base/report-landing-audit.py --lane-repo "$W/lane" --fleet-repo "$W/fleet" \
      --branch master --lane kama --rounds 24 --json > "$OUT/.stdout" 2> "$OUT/.stderr"
  echo "exit=$?"
  if [ -s "$OUT/.stderr" ]; then echo "stderr: $(cat "$OUT/.stderr")"; fi
  python3 - "$OUT/.stdout" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
print("status:", d["summary"]["status"],
      "defects:", [(x["kind"], x["token"]) for r in d["results"] for x in r["defects"]])
PY
  echo
done
rm -f "$OUT/.stdout" "$OUT/.stderr"
